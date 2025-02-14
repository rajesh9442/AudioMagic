import os
import subprocess
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
