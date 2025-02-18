import os
import subprocess
import librosa
import numpy as np
import whisper
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self):
        self.model_name = "htdemucs"
        self.base_dir = os.getcwd()
        self.output_dir = os.path.join(self.base_dir, "separated/demucs")
        os.makedirs(self.output_dir, exist_ok=True)

    def separate_tracks(self, input_path: str):
        """
        Uses Demucs to separate vocals and accompaniment.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # Run Demucs command
        cmd = [
            "demucs", "--two-stems", "vocals",  # Separate only vocals & music
            "-o", self.output_dir,
            input_path
        ]

        try:
            subprocess.run(cmd, check=True)  # Execute Demucs command
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Demucs separation failed: {str(e)}")

        # Extract output file paths
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        demucs_output_path = os.path.join(self.output_dir, "htdemucs", base_name)

        return {
            "vocals": os.path.join(demucs_output_path, "vocals.wav"),
            "accompaniment": os.path.join(demucs_output_path, "no_vocals.wav")
        }

    def process_audio(self, input_path: str):
        """
        Process audio and return paths for both vocals and accompaniment.
        """
        return self.separate_tracks(input_path)

    def generate_meow_vocals(self, vocal_file: str, output_meow_vocal: str):
        """
        Converts the vocal file into meow sounds by adjusting pitch & timing.
        """
        MEOW_FILE = "data/cat/meow.wav"
        SAMPLE_RATE = 44100
        temp_files = []  # Track temp files for cleanup

        print("🔹 Loading Whisper model and transcribing vocal file...")
        model = whisper.load_model("small", device="cpu")
        result = model.transcribe(vocal_file, language="en", word_timestamps=True)

        words_list = []
        for segment in result.get("segments", []):
            for word_data in segment["words"]:
                words_list.append({
                    "word": word_data["word"].strip(),
                    "start": word_data["start"],
                    "end": word_data["end"]
                })

        print("\n🔹 Extracting pitch from vocal file...")
        vocal_y, sr = librosa.load(vocal_file, sr=SAMPLE_RATE)
        vocal_f0, vocal_voiced, _ = librosa.pyin(vocal_y, fmin=librosa.note_to_hz('C2'),
                                                 fmax=librosa.note_to_hz('C7'), sr=sr)
        vocal_times = librosa.times_like(vocal_f0, sr=sr)

        print("\n🔹 Extracting meow sample pitch...")
        meow_y, _ = librosa.load(MEOW_FILE, sr=SAMPLE_RATE)
        meow_f0, meow_voiced, _ = librosa.pyin(meow_y, fmin=librosa.note_to_hz('C2'),
                                               fmax=librosa.note_to_hz('C7'), sr=SAMPLE_RATE)
        if meow_voiced is not None and np.any(meow_voiced):
            ref_meow_pitch = np.nanmean(meow_f0[meow_voiced])  # Get the average pitch
        else:
            ref_meow_pitch = 300  # Fallback value if pitch detection fails

        print(f"🎵 Reference Meow Pitch (Hz): {ref_meow_pitch:.2f}")

        print("\n🔹 Generating meow sounds for each word:")
        meow_audio = AudioSegment.from_file(MEOW_FILE)
        word_meow_segments = []

        for w in words_list:
            start, end = w["start"], w["end"]
            duration = end - start
            indices = np.where((vocal_times >= start) & (vocal_times < end))[0]
            avg_pitch = np.nanmean(vocal_f0[indices]) if indices.size > 0 else None

            if avg_pitch is not None and not np.isnan(avg_pitch):
                pitch_shift = librosa.hz_to_midi(avg_pitch) - librosa.hz_to_midi(ref_meow_pitch)
            else:
                pitch_shift = 0

            temp_out = f"temp_{w['word']}.wav"
            temp_files.append(temp_out)  # Add to temp file tracking

            meow_stretched = stretch_meow_ffmpeg(meow_audio, duration, temp_out)
            final_meow = pitch_shift_segment(meow_stretched, pitch_shift)

            word_meow_segments.append((start, final_meow))

        print(f"\n🔹 Overlaying meows onto a silent track...")
        vocal_duration = librosa.get_duration(path=vocal_file)
        final_meow_audio = AudioSegment.silent(duration=int(vocal_duration * 1000))

        for start, seg in word_meow_segments:
            position = int(start * 1000)
            final_meow_audio = final_meow_audio.overlay(seg, position=position)

        final_meow_audio.export(output_meow_vocal, format="wav")
        print(f"\n✅ Final Meow Vocal File Saved: {output_meow_vocal}")

        # ✅ **Ensure Temp Files are Deleted**
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ Deleted temp file: {temp_file}")
            except Exception as e:
                print(f"❌ Error deleting {temp_file}: {e}")

    def merge_meow_with_instrumental(self, instrumental_file: str, meow_vocal_file: str, output_final_mix: str):
        """
        Merges the meow vocals with the instrumental track.
        """
        print("\n🔹 Loading instrumental and meow vocal tracks...")
        instrumental = AudioSegment.from_file(instrumental_file)
        meow_vocal = AudioSegment.from_file(meow_vocal_file)

        instr_duration = librosa.get_duration(path=instrumental_file)
        meow_duration = librosa.get_duration(path=meow_vocal_file)

        if instr_duration > meow_duration:
            instrumental = instrumental[:int(meow_duration * 1000)]
        elif meow_duration > instr_duration:
            silence = AudioSegment.silent(duration=int((meow_duration - instr_duration) * 1000))
            instrumental = instrumental + silence

        print("\n🔹 Merging meow vocals with instrumental...")
        final_mix = instrumental.overlay(meow_vocal)
        final_mix.export(output_final_mix, format="wav")

        print(f"\n✅ Final Meow Music Saved: {output_final_mix}")


### **🚀 Global Functions (Matches Testing Code Exactly)** ###
def pitch_shift_segment(segment, semitone_shift):
    """Shifts the pitch of a pydub AudioSegment while preserving timing."""
    samples = np.array(segment.get_array_of_samples()).astype(np.float32)
    samples /= 32768.0  # Normalize to -1.0 to 1.0
    shifted = librosa.effects.pitch_shift(samples, sr=segment.frame_rate, n_steps=semitone_shift)
    shifted = np.int16(shifted * 32768)
    return AudioSegment(
        shifted.tobytes(),
        frame_rate=segment.frame_rate,
        sample_width=shifted.dtype.itemsize,
        channels=1
    )

def stretch_meow_ffmpeg(input_audio, target_duration, output_file):
    """Uses FFmpeg to stretch or shrink meow sound to match the target duration."""
    original_duration = len(input_audio) / 1000.0  # Convert ms to sec
    target_duration = max(target_duration, 0.05)
    desired_factor = original_duration / target_duration

    temp_input = "temp_meow.wav"
    input_audio.export(temp_input, format="wav")
    command = ["ffmpeg", "-y", "-i", temp_input, "-filter:a", f"atempo={desired_factor:.3f}", output_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # ✅ **Delete temp_meow.wav after processing**
    if os.path.exists(temp_input):
        os.remove(temp_input)
        print(f"🗑️ Deleted temp file: {temp_input}")

    return AudioSegment.from_file(output_file)
