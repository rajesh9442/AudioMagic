import os
import subprocess
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self):
        self.model_name = "htdemucs"  # Best quality model
        self.base_dir = os.getcwd()  # Ensure base directory is defined
        self.output_dir = os.path.join(self.base_dir, "separated/demucs")  # Set correct path
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory if it doesn't exist

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

    def process_audio(self, input_path: str, mode: str) -> str:
        """
        Process audio and return the separated file path (vocals or accompaniment).
        """
        try:
            tracks = self.separate_tracks(input_path)
            mode_lower = mode.lower()
            if mode_lower in ["vocal", "vocals"]:
                selected_file = tracks["vocals"]
            else:
                selected_file = tracks["accompaniment"]

            return selected_file

        except Exception as e:
            raise RuntimeError(str(e))
