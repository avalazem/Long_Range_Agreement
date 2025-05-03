\
import wave
import contextlib
from pathlib import Path
import pandas as pd
import sys
import os

# Define the base directory for stimuli relative to the script location or workspace root
# Assuming the script is run from the workspace root
stimuli_base_dir = Path("Stimuli/training_auditory")
csv_file_path = stimuli_base_dir / "auditory_training.csv"
wav_dir = stimuli_base_dir / "wavs"

# Check if CSV file exists
if not csv_file_path.is_file():
    print(f"Error: CSV file not found at {csv_file_path}")
    sys.exit(1)

# Check if WAV directory exists
if not wav_dir.is_dir():
    print(f"Error: WAV directory not found at {wav_dir}")
    sys.exit(1)

print(f"Reading trials from: {csv_file_path}")
print(f"Looking for WAV files in: {wav_dir}")

try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)

if 'trial' not in df.columns:
    print(f"Error: 'trial' column not found in {csv_file_path}")
    sys.exit(1)

print("\nVerifying durations:")
all_files_found = True

for trial_name in df['trial']:
    if pd.isna(trial_name):
        print("- Skipping row with missing trial name.")
        continue

    wav_filename = f"{trial_name}.wav"
    wav_filepath = wav_dir / wav_filename

    if not wav_filepath.is_file():
        print(f"- {trial_name}: WAV file not found at {wav_filepath}")
        all_files_found = False
        continue

    try:
        with contextlib.closing(wave.open(str(wav_filepath), 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            if rate > 0:
                duration = frames / float(rate)
                print(f"- {trial_name}: {duration:.3f} seconds")
            else:
                print(f"- {trial_name}: Invalid frame rate (0) in {wav_filepath}")
                all_files_found = False
    except wave.Error as e:
        print(f"- {trial_name}: Could not read WAV file {wav_filepath}: {e}")
        all_files_found = False
    except Exception as e:
         print(f"- {trial_name}: An error occurred processing {wav_filepath}: {e}")
         all_files_found = False

print("\nVerification complete.")
if not all_files_found:
    print("Note: Some files were not found or could not be processed.")

# Also check the trimmed file from the previous step
trimmed_file_path = wav_dir / "trial_16_trimmed.wav"
print(f"\nChecking trimmed file: {trimmed_file_path}")
if trimmed_file_path.is_file():
    try:
        with contextlib.closing(wave.open(str(trimmed_file_path), 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            if rate > 0:
                duration = frames / float(rate)
                print(f"- {trimmed_file_path.name}: {duration:.3f} seconds")
            else:
                print(f"- {trimmed_file_path.name}: Invalid frame rate (0)")
    except wave.Error as e:
        print(f"- {trimmed_file_path.name}: Could not read WAV file: {e}")
    except Exception as e:
         print(f"- {trimmed_file_path.name}: An error occurred processing: {e}")
else:
    print(f"- Trimmed file not found.")

