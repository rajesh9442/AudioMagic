import os
import librosa
import numpy as np
import whisper
from pydub import AudioSegment
from core.utils import pitch_shift_segment, stretch_meow_ffmpeg

class CatVersion:
    def __init__(self):
        self.MEOW_FILE = "data/cat/meow.wav"
        self.SAMPLE_RATE = 44100

    def generate_meow_vocals(self, vocal_file: str, output_meow_vocal: str):
        temp_files = []
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

        print(f"🔍 Total words detected: {len(words_list)}")

        print("\n🔹 Extracting pitch from vocal file...")
        vocal_y, sr = librosa.load(vocal_file, sr=self.SAMPLE_RATE)
        print(f"📊 Vocal waveform shape: {vocal_y.shape}, Sample rate: {sr}")

        # Extract pitch (pyin)
        vocal_f0, _, _ = librosa.pyin(vocal_y, fmin=librosa.note_to_hz('C2'),
                                      fmax=librosa.note_to_hz('C7'), sr=sr)

        # Debug: Check for NaNs and array integrity
        if vocal_f0 is None or np.all(np.isnan(vocal_f0)):
            print("⚠️ No valid pitch data found. Replacing with zeros.")
            vocal_f0 = np.zeros_like(vocal_y)

        print(f"📊 Vocal pitch array shape: {vocal_f0.shape}")
        print(f"🧮 Number of NaN values in vocal_f0: {np.isnan(vocal_f0).sum()}")

        # Create time array
        try:
            vocal_times = librosa.times_like(vocal_f0, sr=sr)
            print(f"⏰ Time array shape: {vocal_times.shape}")
        except Exception as e:
            print("❌ Error creating time array with librosa.times_like")
            print(f"Error: {e}")
            return

        # Meow sample pitch extraction
        print("\n🔹 Extracting meow sample pitch...")
        meow_y, _ = librosa.load(self.MEOW_FILE, sr=self.SAMPLE_RATE)
        meow_f0, meow_voiced, _ = librosa.pyin(meow_y, fmin=librosa.note_to_hz('C2'),
                                               fmax=librosa.note_to_hz('C7'), sr=self.SAMPLE_RATE)
        ref_meow_pitch = np.nanmean(meow_f0[meow_voiced]) if meow_voiced is not None and np.any(meow_voiced) else 300
        print(f"🎵 Reference Meow Pitch (Hz): {ref_meow_pitch:.2f}")

        meow_audio = AudioSegment.from_file(self.MEOW_FILE)
        word_meow_segments = []

        for w in words_list:
            start, end = w["start"], w["end"]
            duration = end - start

            if duration <= 0:
                print(f"⚠️ Skipping zero-length word: {w['word']}")
                continue

            indices = np.where((vocal_times >= start) & (vocal_times < end))[0]
            avg_pitch = np.nanmean(vocal_f0[indices]) if indices.size > 0 else None

            print(f"\n🎤 Processing word: '{w['word']}' | Start: {start:.2f}s | End: {end:.2f}s | Duration: {duration:.2f}s")
            print(f"🎵 Average pitch for word: {avg_pitch if avg_pitch else 'N/A'}")

            pitch_shift = librosa.hz_to_midi(avg_pitch) - librosa.hz_to_midi(ref_meow_pitch) if avg_pitch else 0

            temp_out = f"temp_{w['word']}.wav"
            temp_files.append(temp_out)

            try:
                meow_stretched = stretch_meow_ffmpeg(meow_audio, max(duration, 0.05), temp_out)
                final_meow = pitch_shift_segment(meow_stretched, pitch_shift)
                word_meow_segments.append((start, final_meow))
            except Exception as e:
                print(f"❌ Error processing meow for word '{w['word']}': {e}")

        print(f"\n🔹 Overlaying meows onto a silent track...")
        vocal_duration = librosa.get_duration(path=vocal_file)
        final_meow_audio = AudioSegment.silent(duration=int(vocal_duration * 1000))

        for start, seg in word_meow_segments:
            position = int(start * 1000)
            final_meow_audio = final_meow_audio.overlay(seg, position=position)

        final_meow_audio.export(output_meow_vocal, format="wav")
        print(f"\n✅ Final Meow Vocal File Saved: {output_meow_vocal}")

        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️ Deleted temp file: {temp_file}")

    def merge_meow_with_instrumental(self, instrumental_file: str, meow_vocal_file: str, output_final_mix: str):
        print("\n🔹 Merging meow vocals with instrumental...")
        instrumental = AudioSegment.from_file(instrumental_file)
        meow_vocal = AudioSegment.from_file(meow_vocal_file)

        instr_duration = librosa.get_duration(path=instrumental_file)
        meow_duration = librosa.get_duration(path=meow_vocal_file)

        if instr_duration > meow_duration:
            instrumental = instrumental[:int(meow_duration * 1000)]
        elif meow_duration > instr_duration:
            silence = AudioSegment.silent(duration=int((meow_duration - instr_duration) * 1000))
            instrumental += silence

        final_mix = instrumental.overlay(meow_vocal)
        final_mix.export(output_final_mix, format="wav")
        print(f"\n✅ Final Meow Music Saved: {output_final_mix}")