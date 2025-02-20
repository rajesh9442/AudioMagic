import os
import subprocess
import numpy as np
from pydub import AudioSegment
import librosa

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
    original_duration = len(input_audio) / 1000.0
    target_duration = max(target_duration, 0.05)  # Avoid zero-duration
    desired_factor = original_duration / target_duration

    temp_input = "temp_meow.wav"
    input_audio.export(temp_input, format="wav")
    command = ["ffmpeg", "-y", "-i", temp_input, "-filter:a", f"atempo={desired_factor:.3f}", output_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if os.path.exists(temp_input):
        os.remove(temp_input)
        print(f"🗑️ Deleted temp file: {temp_input}")

    return AudioSegment.from_file(output_file)