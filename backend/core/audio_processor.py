import os
import subprocess
import librosa
import numpy as np
from pydub import AudioSegment
import logging
from core.utils import pitch_shift_segment, stretch_meow_ffmpeg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AudioProcessor:
    def __init__(self):
        self.model_name = "htdemucs"
        self.base_dir = os.getcwd()
        self.output_dir = os.path.join(self.base_dir, "separated")
        os.makedirs(self.output_dir, exist_ok=True)

    def separate_tracks(self, input_path: str):
        """
        Uses Demucs to separate vocals and accompaniment.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        cmd = [
            "demucs", "-n", self.model_name, "--two-stems", "vocals",
            "-o", self.output_dir,
            input_path
        ]

        try:
            logging.debug(f"Running Demucs command: {cmd}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Demucs separation failed: {str(e)}")

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        demucs_output_path = os.path.join(self.output_dir, self.model_name, base_name)

        return {
            "vocals": os.path.join(demucs_output_path, "vocals.wav"),
            "accompaniment": os.path.join(demucs_output_path, "no_vocals.wav")
        }

    def process_audio(self, input_path: str):
        """
        Process audio and return paths for both vocals and accompaniment.
        """
        return self.separate_tracks(input_path)