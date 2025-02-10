# File: core/audio_processor.py
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

    def apply_pitch_shift(self, audio_segment: AudioSegment, n_semitones: int = 4) -> AudioSegment:
        """Custom pitch-shift function."""
        new_sample_rate = int(audio_segment.frame_rate * (2 ** (n_semitones / 12)))
        return audio_segment._spawn(
            audio_segment.raw_data,
            overrides={'frame_rate': new_sample_rate}
        ).set_frame_rate(audio_segment.frame_rate)

    def process_audio(self, input_path: str, mode: str) -> str:
        """Process audio and return output filename."""
        try:
            # Create output folder for Spleeter
            output_folder = os.path.join(os.path.dirname(input_path), "spleeter_output")
            os.makedirs(output_folder, exist_ok=True)

            # Separate tracks
            self.separate_tracks(input_path, output_folder)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # Load separated tracks
            vocals = AudioSegment.from_file(os.path.join(output_folder, base_name, "vocals.wav"))
            accompaniment = AudioSegment.from_file(os.path.join(output_folder, base_name, "accompaniment.wav"))

            # Apply effects
            if mode == "vocals":
                final_audio = vocals
            else:
                final_audio = accompaniment  # Music only

            # Export to upload directory (temp/)
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join(os.path.dirname(input_path), output_filename)
            final_audio.export(output_path, format="mp3")
            
            return output_filename

        except Exception as e:
            print(f"[ERROR] Audio processing failed: {str(e)}")
            raise RuntimeError(str(e))