import os
from spleeter.separator import Separator
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self):
        self.separator = Separator('spleeter:2stems')

    def separate_tracks(self, input_path: str, output_folder: str):
        """Separate vocals and background music."""
        os.makedirs(output_folder, exist_ok=True)
        self.separator.separate_to_file(input_path, output_folder)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        return {
            "vocals": os.path.join(output_folder, base_name, "vocals.wav"),
            "accompaniment": os.path.join(output_folder, base_name, "accompaniment.wav")
        }

    def process_audio(self, input_path: str, mode: str) -> str:
        """Process audio and return the path to the requested track."""
        try:
            output_folder = os.path.join(os.path.dirname(input_path), "spleeter_output")
            os.makedirs(output_folder, exist_ok=True)

            tracks = self.separate_tracks(input_path, output_folder)
            mode_lower = mode.lower()
            if mode_lower in ["vocal", "vocals"]:
                selected_file = tracks["vocals"]
            else:
                selected_file = tracks["accompaniment"]

            return selected_file

        except Exception as e:
            raise RuntimeError(str(e))
