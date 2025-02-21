import os
import librosa
import numpy as np
from pydub import AudioSegment
from core.utils import pitch_shift_segment, stretch_meow_ffmpeg
 
class CatVersion:
    def __init__(self):
        self.MEOW_FILE = "data/cat/meow.wav"
        self.SAMPLE_RATE = 44100
 
    def generate_meow_vocals(self, vocal_file: str, output_meow_vocal: str):
        temp_files = []
        print("🔹 Extracting pitch and amplitude directly from vocal file...")
 
        # Load vocal file
        vocal_y, sr = librosa.load(vocal_file, sr=self.SAMPLE_RATE)
        print(f"📊 Vocal waveform shape: {vocal_y.shape}, Sample rate: {sr}")
 
        # Extract pitch (pyin) and amplitude
        vocal_f0, vocal_voiced_flag, _ = librosa.pyin(
            vocal_y, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'), sr=sr
        )
        vocal_amplitude = librosa.feature.rms(y=vocal_y)[0]
        vocal_times = librosa.times_like(vocal_f0, sr=sr)
 
        # Handle NaNs in pitch extraction
        vocal_f0 = np.where(np.isnan(vocal_f0), 0, vocal_f0)
 
        print(f"🧮 Extracted pitch points: {np.sum(vocal_voiced_flag)}")
        print(f"🧮 Total frames: {len(vocal_f0)}")
 
        # Load Meow sample and extract its pitch
        meow_y, _ = librosa.load(self.MEOW_FILE, sr=self.SAMPLE_RATE)
        meow_f0, meow_voiced, _ = librosa.pyin(
            meow_y, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'), sr=self.SAMPLE_RATE
        )
        ref_meow_pitch = np.nanmean(meow_f0[meow_voiced]) if np.any(meow_voiced) else 300
        print(f"🎵 Reference Meow Pitch (Hz): {ref_meow_pitch:.2f}")
 
        # Convert Meow to Pydub AudioSegment
        meow_audio = AudioSegment.from_file(self.MEOW_FILE)
 
        # Prepare empty audio for final meow track
        vocal_duration = librosa.get_duration(y=vocal_y, sr=sr)
        final_meow_audio = AudioSegment.silent(duration=int(vocal_duration * 1000))
 
        # Adjusted minimum duration for each meow
        min_meow_duration = 0.3  # 300 ms minimum meow sound
 
        # Generate meows based on pitch contour
        for i, pitch in enumerate(vocal_f0):
            if pitch == 0 or not vocal_voiced_flag[i]:
                continue  # Skip unvoiced parts
 
            time_stamp = vocal_times[i]
            amplitude = vocal_amplitude[i] if i < len(vocal_amplitude) else 0.5
 
            # Calculate pitch shift and clip it
            pitch_shift = librosa.hz_to_midi(pitch) - librosa.hz_to_midi(ref_meow_pitch)
            # pitch_shift = np.clip(pitch_shift, -3, 3)
 
            # Use a meaningful frame duration (avoid too short sounds)
            frame_duration = max(librosa.frames_to_time(5, sr=sr), min_meow_duration)
 
            # Stretch meow to match the frame duration
            temp_out = f"temp_meow_{i}.wav"
            temp_files.append(temp_out)
 
            meow_stretched = stretch_meow_ffmpeg(meow_audio, frame_duration, temp_out)
            final_meow = pitch_shift_segment(meow_stretched, pitch_shift)
 
            # Adjust volume based on vocal amplitude
            final_meow = final_meow + (20 * np.log10(amplitude + 1e-6))
 
            # Overlay meow onto final track
            position = int(time_stamp * 1000)
            final_meow_audio = final_meow_audio.overlay(final_meow, position=position)
 
        # Export final meow vocals
        final_meow_audio.export(output_meow_vocal, format="wav")
        print(f"\n✅ Final Meow Vocal File Saved: {output_meow_vocal}")
 
        # Cleanup temp files
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
 
        # Align durations
        if instr_duration > meow_duration:
            instrumental = instrumental[:int(meow_duration * 1000)]
        elif meow_duration > instr_duration:
            silence = AudioSegment.silent(duration=int((meow_duration - instr_duration) * 1000))
            instrumental += silence
 
        # Overlay meows on instrumental
        final_mix = instrumental.overlay(meow_vocal)
        final_mix.export(output_final_mix, format="wav")
        print(f"\n✅ Final Meow Music Saved: {output_final_mix}")