import os
from spleeter.separator import Separator
from pydub import AudioSegment
from pydub.effects import pitch_shift

# Step 1: Initialize Spleeter Separator
# Use the '2stems' model (vocals and accompaniment)
separator = Separator('spleeter:2stems')

# Step 2: Define input and output paths
input_audio = 'input_audio.mp3'  # Replace with your input file
output_folder = 'output_folder'  # Folder to store separated tracks

# Step 3: Separate vocals and accompaniment
separator.separate_to_file(input_audio, output_folder)

# Step 4: Load separated tracks
vocals_path = os.path.join(output_folder, os.path.splitext(os.path.basename(input_audio))[0], 'vocals.wav')
accompaniment_path = os.path.join(output_folder, os.path.splitext(os.path.basename(input_audio))[0], 'accompaniment.wav')

vocals = AudioSegment.from_file(vocals_path)
accompaniment = AudioSegment.from_file(accompaniment_path)

# Step 5: Modify vocals to sound like a cat's meow
# Use pitch shifting to achieve the effect
vocals_modified = pitch_shift(vocals, n_semitones=4)  # Increase pitch by 4 semitones

# Step 6: Merge modified vocals and accompaniment
final_audio = vocals_modified.overlay(accompaniment)

# Step 7: Export the final audio
final_audio.export('final_audio.mp3', format='mp3')

print("Processing complete! Final audio saved as 'final_audio.mp3'.")