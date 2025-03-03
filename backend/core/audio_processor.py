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

    def separate_tracks(self, input_path: str, temp_folder: str):
        """
        Uses Demucs to separate vocals and accompaniment.
        Now uses the temp folder as the output directory.
        """
        demucs_output = os.path.join(temp_folder, "demucs")
        os.makedirs(demucs_output, exist_ok=True)
        
        logging.info(f"Using model: {self.model_name}")
        logging.info(f"Demucs output directory: {demucs_output}")

        cmd = [
            "demucs", "-n", self.model_name, "--two-stems", "vocals",
            "-o", demucs_output, "--mp3",
            input_path
        ]

        try:
            logging.debug(f"Running Demucs command: {cmd}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Demucs separation failed: {str(e)}")

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        demucs_output_path = os.path.join(demucs_output, self.model_name, base_name)

        return {
            "vocals": os.path.join(demucs_output_path, "vocals.mp3"),
            "accompaniment": os.path.join(demucs_output_path, "no_vocals.mp3")
        }

    def process_audio(self, input_path: str, temp_folder: str):
        """
        Process audio and return paths for both vocals and accompaniment.
        """
        return self.separate_tracks(input_path, temp_folder)