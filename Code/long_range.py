# '''
# Long-Range sentence presentation experiment using expyriment.
# Based on swp.py and adapted for sentence-level stimuli (visual or auditory).

# Project: Long-Range Agreement Pilot
# Author: Ali Al-Azem

# Usage: python long_range.py <stimulus folder>
# Example: python long_range.py ../Stimuli/subject_01//sub_01_run_1
# '''

import sys
import re
from pathlib import Path
import pandas as pd
from expyriment import design, control, stimuli, misc, io
import argparse
import random # Import random explicitly

script_dir = Path(__file__).parent.resolve()

# --- Argument Parsing ---
# Moved and consolidated argument parsing to the beginning of the script.
parser = argparse.ArgumentParser(
    description="Long-Range Agreement Experiment. \\nUsage: python long_range.py <run_folder_path> [--invert_hands]",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "run_folder_path",
    type=str,
    help="Path to the directory containing the stimulus CSV file and .wav audio files.\\n(e.g., ../Stimuli/subject_01/visual/sub1_run1_visual)"
)
parser.add_argument(
    "--invert_hands",
    action="store_true",
    help="Use inverted hands instruction image."
)
args = parser.parse_args() # Parse arguments at the beginning

# --- Use parsed arguments ---
# run_folder_path is now taken from the parsed arguments.
run_folder_path = Path(args.run_folder_path).resolve()
# args.invert_hands will be used later where it's already correctly referenced.


# Experiment Parameters
DEBUG = False  # Set to False for fullscreen, True for development mode
INITIAL_WAIT = 2000  # ms, Wait time after instructions before first trigger/trial
FINAL_WAIT = 10000   # ms, Wait time at the end of the experiment
TEXT_SIZE = 50 
TEXT_FONT =  str(script_dir / 'Inconsolata-Regular.ttf')  # Font for sentence presentation
PROBE_SIZE = 50
PROBE_FONT = str(script_dir / 'Inconsolata-Regular.ttf') # Font for probe presentation
LEFT_HAND_KEY =  misc.constants.K_y # Key to press after sentence presentation (Use constant)
RIGHT_HAND_KEY = misc.constants.K_f # "                                                     "
TRIGGER_KEY = misc.constants.K_t# fMRI trigger key
NUM_TRIGGERS = 3 # Number of triggers to wait for
ESCAPE_KEY = misc.constants.K_ESCAPE # Key to exit the experiment
CONTROLLER_KEY = misc.constants.K_SPACE # Key for experimenter to start after instructions

# Timing Parameters (modify as needed)
STIMULUS_ONTIME = 200           # ms, Duration each word is shown (visual) (like params.stimulus_ontime)
STIMULUS_ITI = 200              # ms, Duration of the inter-stimulus interval (like params.stimulus_iti)
SOA_PROBE = 1000                # ms, Fixation duration AFTER sentence BEFORE probe for both modalities (added to last ITI for integer reasons...)
CUE_DURATION = 1000             # ms, Duration of the input modality cues (visual/auditory)
PROBE_DURATION = 1000           # ms, Duration of the probe (based on 'Neural Populations' paper)
RESPONSE_DURATION = 2000        # ms, Within rest period, how long to wait for a response AFTER probe
AUDIO_DURATION = 4000           # ms, Duration of the audio stimulus (like params.audio_duration)
# ----------------------------------------

# Determine modality and base paths
if not run_folder_path.is_dir():
    print(f"Error: Run folder not found or is not a directory: {run_folder_path}")
    sys.exit(1)

# --- Find the stimulus CSV file within the run folder ---
csv_files = list(run_folder_path.glob('*.csv'))
if not csv_files:
    print(f"Error: No CSV file found in the specified run folder: {run_folder_path}")
    sys.exit(1)
elif len(csv_files) > 1:
    print(f"Warning: Multiple CSV files found in {run_folder_path}. Using the first one: {csv_files[0]}")
stim_file_path = csv_files[0]
# ---------------------------------------------------------

# --- Load Stimuli CSV to determine modality ---
try:
    stim_df = pd.read_csv(stim_file_path)
    # Ensure 'modality' column exists
    if 'modality' not in stim_df.columns:
        print(f"Error: Stimulus CSV missing required 'modality' column: {stim_file_path}")
        sys.exit(1)
    # Determine modality from the first row (assuming consistent per file)
    modality = stim_df['modality'].iloc[0].lower()
    if modality not in ['visual', 'auditory']:
        print(f"Error: Invalid modality '{modality}' found in CSV column: {stim_file_path}")
        print("Expected 'visual' or 'auditory'.")
        sys.exit(1)
except Exception as e:
    print(f"Error reading stimulus CSV file or determining modality: {e}")
    sys.exit(1)
# -----------------------------------------------------


# Infer base directories from the run folder path
try:
    # Assumes path structure like ../Stimuli/subject_XX/run_Y
    parts = run_folder_path.parts
    # modality = parts[-2] # <-- REMOVED: Modality now comes from CSV
    stimuli_base_dir = run_folder_path # The run folder is the base for stimuli (CSV, audio)
    subject_dir = run_folder_path.parents[1] # ../Stimuli/subject_XX
    project_root = run_folder_path.parents[2] # /home/avalazem/Desktop/Work/Single_Word_Processing_Stage/Long_Range_Agreement/Long_Range_Pilot
    log_dir = project_root / "Logs"
    log_dir.mkdir(exist_ok=True) # Ensure log directory exists
    # Correct the image directory path to include "Stimuli"
    image_dir = project_root / "Stimuli" / "Input_Images"

    # Infer subject ID and run number from the CSV filename found
    filename_match = re.match(r"sub_(train|\d{2})_run_(\d+)\.csv$", stim_file_path.name, re.IGNORECASE)
    if not filename_match:
        print(f"Error: Could not extract subject ID and run number from CSV filename: {stim_file_path.name}")
        print("Expected CSV filename format like: sub_XX_run_Y.csv (e.g., sub_01_run_1.csv) or sub_train_run_Y.csv") # Updated expected format message
        sys.exit(1)
    subject_id = filename_match.group(1) # This will be 'train' or 'XX'
    run_number = filename_match.group(2)

except IndexError:
    print(f"Error: Could not determine base paths from run folder path: {run_folder_path}")
    print("Expected structure like: ../Stimuli/subject_XX/some_folder/subXX_runY_folder")
    sys.exit(1)

print(f"Subject ID: {subject_id}")
print(f"Run Number: {run_number}")
print(f"Stimulus File: {stim_file_path}")
print(f"Stimuli Base Directory: {stimuli_base_dir}")
print(f"Log Directory: {log_dir}")

# --- Load Stimuli ---
try:
    # stim_df = pd.read_csv(stim_file_path) # Already loaded above to get modality
    # Ensure required columns exist
    required_cols = ['sentence', 'structure', 'probe_word', 'modality']
   
    if not all(col in stim_df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in stim_df.columns]
        print(f"Error: Stimulus CSV missing required columns: {missing} in {stim_file_path}")
        sys.exit(1)
except Exception as e:
    print(f"Error checking stimulus CSV columns: {e}")
    sys.exit(1)

# Extract Num Trials
num_trials = len(stim_df)


# --- Expyriment Setup ---
exp = design.Experiment(name=f"Long-Range Agreement - Sub {subject_id} Run {run_number})", text_size=TEXT_SIZE)
control.defaults.initialize_delay = 0 # Avoids initial pause screen
if DEBUG:
    control.set_develop_mode(on=True, window_size=(800, 600))
control.initialize(exp)

# --- Prepare Stimuli Objects ---
fixation_cross = stimuli.FixCross(size=(50, 50), line_width=4)
blank_screen = stimuli.BlankScreen()
ready_text = "Waiting for scanner sync (or press \'t\')"
end_text = f"Fin de cette partie. Merci!"

# --- Preload Static Stimuli ---
fixation_cross.preload()
blank_screen.preload()

# Preload instruction/feedback text screens
# Instructions
# Determine instruction image based on --invert_hands argument
instruction_image_path = Path(image_dir) / ("instructions_invert-hands.png" if args.invert_hands else "instructions.png")
instructions = stimuli.Picture(str(instruction_image_path))
instructions.scale_to_fullscreen()
instructions.preload()

# Preload modality cues
visual_cue_path = Path(image_dir) / "visual_cue.png"
auditory_cue_path = Path(image_dir) / "auditory_cue.png"
visual_cue = stimuli.Picture(str(visual_cue_path))
auditory_cue = stimuli.Picture(str(auditory_cue_path))
visual_cue.preload()
auditory_cue.preload()
modality_cues = {'visual': visual_cue, 'auditory': auditory_cue} # Store cues in a dict

# Preload ready and end text screens
stimuli.TextLine(ready_text).preload()
stimuli.TextScreen("Fin", end_text).preload()

# --- Preload Trial Stimuli ---
preloaded_stimuli = {} # Dictionary to hold preloaded stimuli for each trial
preloaded_word_counts = {} # Dictionary to hold word counts for visual trials
preloaded_rest_durations = {} # Dictionary to hold trial durations

for index, trial_data in stim_df.iterrows():
    # Use 1-based index for trial ID and filename, matching row number
    trial_id_one_based = index + 1
    sentence = trial_data['sentence']
    current_modality = trial_data['modality'].lower() # Get modality for this specific 
    
    # Preload the trial duration (ITI)
    if current_modality == 'visual':
        # ... existing visual preload ...
        sentence_text = sentence.rstrip('.') # Remove trailing period
        words = re.findall(r"[\w'-]+|[.,!?;:]", sentence_text) # Split words and punctuation
        preloaded_word_counts[trial_id_one_based] = len(words) # Store word count
        trial_stim_list = []
        for word in words:
            stim = stimuli.TextLine(word, text_size=TEXT_SIZE, text_font=TEXT_FONT)
            stim.preload()
            trial_stim_list.append(stim)
        preloaded_stimuli[trial_id_one_based] = trial_stim_list # Use 1-based index as key

    elif current_modality == 'auditory':
        # --- Use the 'trial' column value for the filename ---
        if 'trial' not in trial_data:
            print(f"Error: 'trial' column missing in input CSV for row index {index}. Cannot determine audio filenames.")
            preloaded_stimuli[trial_id_one_based] = (None, None) # Store tuple indicating failure
            preloaded_word_counts[trial_id_one_based] = 0
            continue # Skip to next iteration

        trial_identifier = trial_data['trial'] # Get value like 'trial_1'
        wav_filename = f"{trial_identifier}.wav" # Construct sentence filename
        probe_wav_filename = f"{trial_identifier}_probe.wav" # Construct probe filename
        # ----------------------------------------------------

        # Look for audio files in an 'wavs' subfolder of the run folder
        wav_dir = stimuli_base_dir / "wavs" # Ensure this matches your folder name
        wav_path = wav_dir / wav_filename
        probe_wav_path = wav_dir / probe_wav_filename

        # Preload Sentence Audio
        audio_stim = None
        if wav_path.is_file():
            try:
                audio_stim = stimuli.Audio(str(wav_path))
                audio_stim.preload()
            except Exception as e:
                print(f"Warning: Could not preload sentence audio file {wav_path}: {e}")
                audio_stim = None # Mark as failed preload
        else:
            print(f"Warning: Sentence audio file not found during preload for trial {trial_id_one_based}: {wav_path}")
            audio_stim = None # Mark as not found

        # Preload Probe Audio
        probe_audio_stim = None
        if probe_wav_path.is_file():
            try:
                probe_audio_stim = stimuli.Audio(str(probe_wav_path))
                probe_audio_stim.preload()
            except Exception as e:
                print(f"Warning: Could not preload probe audio file {probe_wav_path}: {e}")
                probe_audio_stim = None # Mark as failed preload
        else:
            print(f"Warning: Probe audio file not found during preload for trial {trial_id_one_based}: {probe_wav_path}")
            probe_audio_stim = None # Mark as not found

        preloaded_stimuli[trial_id_one_based] = (audio_stim, probe_audio_stim) # Store tuple of preloaded objects (or None)
        preloaded_word_counts[trial_id_one_based] = 0 # Store 0 for auditory trials

# --- Calculate Trial Timings and Total Duration ---
expected_total_duration = INITIAL_WAIT
target_onset_times = {}
current_target_onset = INITIAL_WAIT # Target start for the first trial block
previous_modality_for_timing = None

for index, trial_data in stim_df.iterrows():
    trial_id_one_based = index + 1
    current_modality = trial_data['modality'].lower()

    # Store the target onset for the START of this trial's block
    target_onset_times[trial_id_one_based] = current_target_onset

    # Calculate duration of potential cue/fixation for THIS trial
    cue_fix_duration = 0
    if index == 0 or current_modality != previous_modality_for_timing:
        cue_fix_duration = CUE_DURATION

    # Calculate the duration of the stimulus presentation + probe + response window
    word_count = preloaded_word_counts.get(trial_id_one_based, 0)
    if current_modality == 'visual':
        trial_stim_probe_duration = (word_count * STIMULUS_ONTIME) + (word_count * STIMULUS_ITI) + SOA_PROBE + PROBE_DURATION
    elif current_modality == 'auditory':
        trial_stim_probe_duration = AUDIO_DURATION + SOA_PROBE + PROBE_DURATION
    else:
        trial_stim_probe_duration = 0 # Should not happen

    preloaded_rest_durations[trial_id_one_based] = trial_data['rest_duration'] * 1000 # Get the trial duration from the CSV
    
    # Get ITI for this trial (assigned rest duration)
    current_iti = preloaded_rest_durations[trial_id_one_based]

    # Calculate the start time for the next trial's block
    # Add this trial's cue/fix duration, stim/probe duration, and ITI
    current_target_onset += cue_fix_duration + trial_stim_probe_duration + current_iti

    # Update modality for next iteration's cue_fix_duration calculation
    previous_modality_for_timing = current_modality

# Adjust expected total duration calculation
# The last 'current_target_onset' is the start time of the hypothetical trial AFTER the last one.
# So, it represents the end of the last trial's ITI.
expected_total_duration = current_target_onset + FINAL_WAIT # Add final wait buffer

print(f"Subject ID: {subject_id}")
print(f"Run Number: {run_number}")
print(f"Total number of trials: {num_trials}")
print(f"Expected Total duration: {expected_total_duration / 1000.0:.2f} s")

# --- Experiment Flow ---
control.start(skip_ready_screen=True)

# Display instructions
instructions.present()
exp.keyboard.wait(CONTROLLER_KEY) # Wait for CONTROLLER_KEY to start

# Ready screen and wait for trigger
stimuli.TextLine(ready_text).present()
if not DEBUG:
    for _ in range(NUM_TRIGGERS):  # Wait for trigger key NUM_TRIGGERS times
        exp.keyboard.wait(TRIGGER_KEY)
else:
    exp.clock.wait(1000)  # Short wait in debug mode

start_time = exp.clock.time
fixation_cross.present()
exp.clock.wait(INITIAL_WAIT)

# --- Setup Logging ---
# Use subject ID and run number for log file name
log_filename = log_dir / f"subject_{subject_id}_LRA_{run_number}.csv"
# Use 1-based TrialNumber instead of TrialID which might be confusing
exp.data_variable_names = ["TrialNumber", "TrialOnset_ms", "Sentence", "Structure", "Modality", "StimulusDuration_ms", "KEY", "RT_ms"]

# --- Main Trial Loop ---
print("Starting main trial loop...") # Added for clarity
previous_modality = None # Keep track of modality across trials

for index, trial_data in stim_df.iterrows():
    sentence = trial_data['sentence']
    structure = trial_data['structure']
    current_modality = trial_data['modality'].lower()
    probe_word = trial_data['probe_word'].upper() # <-- Get probe word and convert to uppercase to differentiate low-level perceptions
    # Use 1-based index for trial number identification and logging
    trial_id_one_based = index + 1 # This is the CURRENT trial number in the loop

    # --- Wait until the target onset time for THIS ENTIRE BLOCK --- (Moved to top)
    target_onset = target_onset_times.get(trial_id_one_based, -1)
    if target_onset > 0:
        while exp.clock.time - start_time < target_onset:
            # Actively wait (yields processing time)
            exp.keyboard.check(process_control_events=True) # Check for escape key etc.
            if exp.keyboard.check(ESCAPE_KEY): # Check again inside loop
                 control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                 sys.exit()
            pass # Keep looping until target time is reached
    # -----------------------------------------------------------

    # --- Timing Verification (Print AFTER initial wait) --- (Moved up)
    actual_onset = exp.clock.time - start_time # Time block actually starts
    stimulus_actual_duration_ms = -1.0 # Initialize stimulus duration for logging

    delta = actual_onset - target_onset
    warn = " !!!" if delta > 25 else "" # Adjusted warning threshold slightly
    # Print timing info for the *current* trial block start
    print(f"Trial {trial_id_one_based} Target: {target_onset:.2f} Actual: {actual_onset:.2f} Delta: {delta:.2f}{warn}")
    # ----------------------------------------------------

    # --- Display Modality Cue and subsequent Fixation if Changed --- (Now after onset wait)
    if index == 0 or current_modality != previous_modality:
        print(f"Presenting cue for modality: {current_modality}") # Debug print
        cue_to_present = modality_cues.get(current_modality)
        if cue_to_present:
            cue_to_present.present()
            # Wait for CUE_DURATION, checking for escape
            wait_end_time = exp.clock.time + CUE_DURATION
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU

            # Present fixation cross AFTER cue
            fixation_cross.present()
            # Wait for CUE_DURATION, checking for escape
            wait_end_time = exp.clock.time + CUE_DURATION
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU
        else:
            print(f"Warning: Could not find preloaded cue for modality '{current_modality}'")
            # Optionally, present a default (like fixation) and wait anyway
            fixation_cross.present()
            exp.clock.wait(CUE_DURATION) # Wait the full combined duration
    # -------------------------------------------------------------

    # Retrieve preloaded stimulus using the 1-based index
    current_stim_data = preloaded_stimuli.get(trial_id_one_based)

    # Skip trial if stimulus failed to load/preload
    if current_stim_data is None:
         print(f"Skipping trial {trial_id_one_based} due to missing/failed stimulus data.")
         exp.data.add([trial_id_one_based, actual_onset, sentence, structure, current_modality, stimulus_actual_duration_ms, "NO_STIM_DATA", -3]) # MODIFIED
         previous_modality = current_modality # Update modality even if skipped
         # Need to wait for the ITI duration even if skipped
         fixation_cross.present()
         current_rest = preloaded_rest_durations[index]
         exp.clock.wait(current_rest)
         continue

    # 1. Stimulus Presentation (Starts immediately after cue/fixation or onset wait)
    stimulus_start_time = exp.clock.time # Log actual stimulus start time
    stimulus_end_time = 0
    if current_modality == 'visual':
        visual_stim_list = current_stim_data
        for i, stim in enumerate(visual_stim_list):
            stim.present()
            word_onset_time = exp.clock.time # Time the word appeared
            # Wait for STIMULUS_ONTIME duration, checking for escape
            wait_end_time = exp.clock.time + STIMULUS_ONTIME
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU

            # Present blank screen for IWI_DURATION after each word (including last)
            blank_screen.present()
            # Wait for STIMULUS_ITI duration, checking for escape
            wait_end_time = exp.clock.time + STIMULUS_ITI
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU

        stimulus_end_time = exp.clock.time # End time is after last word's IWI wait
        if stimulus_start_time > 0 and stimulus_end_time > stimulus_start_time:
            stimulus_actual_duration_ms = stimulus_end_time - stimulus_start_time

    elif current_modality == 'auditory':
        sentence_audio, probe_audio = current_stim_data # Unpack the tuple

        # Check if sentence audio is valid before proceeding
        if sentence_audio is None:
            print(f"Skipping trial {trial_id_one_based} due to missing sentence audio.")
            exp.data.add([trial_id_one_based, actual_onset, sentence, structure, current_modality, stimulus_actual_duration_ms, "NO_SENT_AUDIO", -2]) # MODIFIED
            # Go directly to Rest duration for this trial
            blank_screen.present()
            current_rest = preloaded_rest_durations[index] # Rest still uses 0-based index
            exp.clock.wait(current_rest)
            continue # Skip rest of trial logic

        # Present Sentence Audio
        try:
            fixation_cross.present() # Keep fixation during audio
            audio_filename_to_play = getattr(sentence_audio, 'filename', 'N/A')
            audio_play_start_time = exp.clock.time
            sentence_audio.play() # Start playing audio (non-blocking)

            # Wait for AUDIO_DURATION, checking for escape periodically
            wait_end_time = exp.clock.time + AUDIO_DURATION
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    sentence_audio.stop()
                    if probe_audio: probe_audio.stop() # Stop probe too if loaded
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                # Wait for a short interval before checking again
                exp.clock.wait(10) # Check every 10ms

            # Ensure the loop finishes close to the target time, handle potential overshoot
            remaining_wait = wait_end_time - exp.clock.time
            if remaining_wait > 0:
                exp.clock.wait(remaining_wait)

            sentence_audio.stop() # Stop playback immediately after AUDIO_DURATION
            stimulus_end_time = exp.clock.time # End time is right after audio stops
            if stimulus_start_time > 0 and stimulus_end_time > stimulus_start_time:
                stimulus_actual_duration_ms = stimulus_end_time - stimulus_start_time
        except Exception as e:
            print(f"Error presenting preloaded sentence audio for trial {trial_id_one_based}: {e}")
            exp.data.add([trial_id_one_based, actual_onset, sentence, structure, current_modality, stimulus_actual_duration_ms, "SENT_AUDIO_ERR", -2]) # MODIFIED
            # Go directly to Rest duration for this trial
            blank_screen.present()
            current_rest = preloaded_rest_durations[index] # Rest still uses 0-based index
            exp.clock.wait(current_rest)
            continue # Skip rest of trial logic

    # 2. Post-Stimulus Fixation (SOA_PROBE)
    exp.clock.wait(SOA_PROBE)
    post_stim_fixation_end_time = exp.clock.time

    # 3. Probe Presentation & Response Window
    keys = None
    rt = None
    logged_key = "ERROR" # Default to error, overwrite on success
    logged_rt = -999    # Default to error, overwrite on success
    probe_presentation_end_time = -1 # Initialize

    if current_modality == 'visual':
        # --- Visual Probe ---
        current_probe = stimuli.TextLine(probe_word, text_size=PROBE_SIZE, text_font=PROBE_FONT)
        current_probe.present()
        probe_presentation_start_time = exp.clock.time

        # Wait for PROBE_DURATION (presentation only), checking for ESCAPE
        wait_end_probe_presentation = probe_presentation_start_time + PROBE_DURATION
        escaped_during_probe = False
        while exp.clock.time < wait_end_probe_presentation:
            if exp.keyboard.check(ESCAPE_KEY):
                escaped_during_probe = True
                break
            exp.clock.wait(1) # yield to other processes, check often

        if escaped_during_probe:
            control.end(goodbye_text="Experiment aborted during visual probe.", goodbye_delay=1000)
            sys.exit()
        
        probe_presentation_end_time = exp.clock.time # Mark end of visual probe presentation

        # Probe presentation finished. RT starts from now.
        # Present fixation cross during the response window.
        fixation_cross.present()
        
        # Collect response during RESPONSE_DURATION
        # rt will be relative to the start of this call (i.e., from probe_presentation_end_time).
        keys, rt = exp.keyboard.wait(keys=[LEFT_HAND_KEY, RIGHT_HAND_KEY, ESCAPE_KEY], duration=RESPONSE_DURATION)
        
        # keys could be a key constant or None if timeout. rt is ms or None.

    elif current_modality == 'auditory':
        # --- Auditory Probe ---
        fixation_cross.present() # Keep fixation during auditory probe

        if probe_audio is not None:
            try:
                probe_audio.play()
                probe_presentation_start_time = exp.clock.time

                # Wait for PROBE_DURATION (presentation only), checking for ESCAPE
                wait_end_probe_presentation = probe_presentation_start_time + PROBE_DURATION
                escaped_during_probe = False
                while exp.clock.time < wait_end_probe_presentation:
                    # Check if audio finished playing; if so, just continue waiting out PROBE_DURATION
                    if not probe_audio.is_playing and exp.clock.time < wait_end_probe_presentation:
                        # Audio finished early, but we wait for full PROBE_DURATION
                        pass
                    if exp.keyboard.check(ESCAPE_KEY):
                        escaped_during_probe = True
                        break
                    exp.clock.wait(1) # yield

                probe_audio.stop() # Ensure audio stops if it was still playing

                if escaped_during_probe:
                    control.end(goodbye_text="Experiment aborted during auditory probe.", goodbye_delay=1000)
                    sys.exit()
                
                probe_presentation_end_time = exp.clock.time # Mark end of auditory probe presentation
                
                # Probe presentation finished. RT starts from now.
                # Fixation cross should still be visible.
                # Collect response during RESPONSE_DURATION
                keys, rt = exp.keyboard.wait(keys=[LEFT_HAND_KEY, RIGHT_HAND_KEY, ESCAPE_KEY], duration=RESPONSE_DURATION)

            except Exception as e:
                print(f"Error playing probe audio for trial {trial_id_one_based}: {e}")
                # Attempt to maintain timing integrity even if audio fails
                # Simulate probe presentation duration
                current_time = exp.clock.time
                simulated_probe_end = current_time + PROBE_DURATION
                while exp.clock.time < simulated_probe_end:
                    if exp.keyboard.check(ESCAPE_KEY): # Still allow escape
                        control.end(goodbye_text="Experiment aborted during audio error handling.", goodbye_delay=1000)
                        sys.exit()
                    exp.clock.wait(1)
                probe_presentation_end_time = exp.clock.time
                
                # Simulate response duration (and collect keys if any)
                keys, rt = exp.keyboard.wait(keys=[LEFT_HAND_KEY, RIGHT_HAND_KEY, ESCAPE_KEY], duration=RESPONSE_DURATION)
                logged_key = "PROBE_AUDIO_ERR"
                logged_rt = -4 # Indicate probe audio error

        else: # Probe audio was missing or failed to preload
            print(f"Probe audio missing for trial {trial_id_one_based}. Presenting fixation for probe duration.")
            fixation_cross.present()
            # Wait for PROBE_DURATION (silent presentation)
            current_time = exp.clock.time
            simulated_probe_end = current_time + PROBE_DURATION
            while exp.clock.time < simulated_probe_end:
                if exp.keyboard.check(ESCAPE_KEY): # Still allow escape
                    control.end(goodbye_text="Experiment aborted during missing audio handling.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1)
            probe_presentation_end_time = exp.clock.time

            # Collect response during RESPONSE_DURATION
            keys, rt = exp.keyboard.wait(keys=[LEFT_HAND_KEY, RIGHT_HAND_KEY, ESCAPE_KEY], duration=RESPONSE_DURATION)
            logged_key = "NO_PROBE_AUDIO"
            logged_rt = -5 # Indicate missing probe audio file

    # --- Process Response ---
    if keys == ESCAPE_KEY: # Check if escape was pressed during RESPONSE_DURATION
        control.end(goodbye_text="Experiment aborted by user during response window.", goodbye_delay=1000)
        sys.exit()

    # RT is relative to the start of the RESPONSE_DURATION window.
    # Only update logged_key/rt if they weren't set by specific error conditions above (PROBE_AUDIO_ERR, NO_PROBE_AUDIO)
    if logged_key == "ERROR": # Default value, means no specific error was logged for key/rt yet
        if keys is None: # Timeout during RESPONSE_DURATION
            logged_key = "TIMEOUT"
            logged_rt = -1 # Using -1 for timeout, as expyriment rt is None for timeout. -999 was previous.
        elif keys == LEFT_HAND_KEY:
            logged_key = 'left'
            logged_rt = rt 
        elif keys == RIGHT_HAND_KEY:
            logged_key = 'right'
            logged_rt = rt
        # else: logged_key remains "ERROR" and logged_rt -999 if unexpected key or situation.

    # The response window is finished.
    response_window_actual_end_time = exp.clock.time

    # 4. Log Data
    # Log the string representation of the key and the RT.
    # actual_onset was captured at the beginning of the trial block.
    # stimulus_actual_duration_ms was calculated after stimulus presentation or remains -1.0
    exp.data.add([trial_id_one_based, actual_onset, sentence, structure, current_modality, stimulus_actual_duration_ms, logged_key, logged_rt])

    # Update previous modality for the next iteration AFTER processing the current trial
    previous_modality = current_modality

    # 5. Inter-Trial Interval (ITI) - Dynamic Wait Calculation
    # This section now handles the "ITI_proper", which is the time remaining from
    # the RestDurationFromCSV after RESPONSE_DURATION has occurred.
    # The target_onset_times logic correctly calculates the required wait time
    # from the end of the response window to the start of the next trial.
    fixation_cross.present() 

    if trial_id_one_based < num_trials: # Corrected: Use trial_id_one_based instead of next_trial_index
        # --- ITI for non-last trials ---
        target_onset_next_trial = target_onset_times.get(trial_id_one_based + 1, -1)
        if target_onset_next_trial > 0:
            current_time_after_response_window = exp.clock.time - start_time
            required_fixation_wait = target_onset_next_trial - current_time_after_response_window

            if required_fixation_wait < 0:
                print(f"Warning: Trial {trial_id_one_based} block overran expected end time. Setting ITI fixation wait to 0.")
                required_fixation_wait = 0
            
            wait_end_time = exp.clock.time + required_fixation_wait
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    # Ensure data is saved if aborted during ITI
                    # Corrected data saving on abort during ITI
                    data_file = io.DataFile(filename=log_filename)
                    data_file.add(exp.data)
                    data_file.save()
                    control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU
        else:
             print(f"Warning: Could not get target onset for next trial {trial_id_one_based + 1}. Using default ITI.")
             default_iti = preloaded_rest_durations[index] # Use assigned rest as fallback
             wait_end_time = exp.clock.time + default_iti
             while exp.clock.time < wait_end_time:
                 if exp.keyboard.check(ESCAPE_KEY):
                     # Ensure data is saved if aborted during ITI
                     # Corrected data saving on abort during ITI
                     data_file = io.DataFile(filename=log_filename)
                     data_file.add(exp.data)
                     data_file.save()
                     control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
                     sys.exit()
                 exp.clock.wait(1)
    else:
        # --- ITI for the LAST trial ---
        rest_duration_from_csv = preloaded_rest_durations[index] # index is num_trials - 1 here
        
        # ITI_proper for the last trial:
        actual_fixation_for_last_trial = rest_duration_from_csv - RESPONSE_DURATION
        if actual_fixation_for_last_trial < 0:
            print(f"Warning: Last trial's configured rest duration ({rest_duration_from_csv}ms) is less than RESPONSE_DURATION ({RESPONSE_DURATION}ms). Final fixation will be 0ms.")
            actual_fixation_for_last_trial = 0
            
        wait_end_time = exp.clock.time + actual_fixation_for_last_trial
        while exp.clock.time < wait_end_time:
            if exp.keyboard.check(ESCAPE_KEY):
                # Ensure data is saved if aborted during final ITI
                data_file = io.DataFile(filename=log_filename)
                data_file.add(exp.data)
                data_file.save()
                control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
                sys.exit()
            exp.clock.wait(1) # Wait 1ms to yield CPU
        # The loop finishes, and the code proceeds to the end-of-experiment section

# --- End of Main Trial Loop ---

# Calculate the expected end time of the last trial's activity
last_trial_target_onset = target_onset_times.get(num_trials, -1)
if last_trial_target_onset > 0:
    last_trial_data = stim_df.iloc[-1]
    last_modality = last_trial_data['modality'].lower()
    last_word_count = preloaded_word_counts.get(num_trials, 0)
    last_trial_rest_duration = preloaded_rest_durations[num_trials - 1] # Get the rest duration assigned to the last trial

    if last_modality == 'visual':
        last_trial_stim_probe_duration = (last_word_count * STIMULUS_ONTIME) + (last_word_count * STIMULUS_ITI) + SOA_PROBE + PROBE_DURATION
    elif last_modality == 'auditory':
         last_trial_stim_probe_duration = AUDIO_DURATION + SOA_PROBE + PROBE_DURATION
    else:
        last_trial_stim_probe_duration = 0

    # Calculate when the last trial's activity (stim + probe) ends
    expected_end_of_last_trial_activity = last_trial_target_onset + last_trial_stim_probe_duration
    # Add the last trial's specific rest duration
    expected_end_of_last_trial_plus_rest = expected_end_of_last_trial_activity + last_trial_rest_duration
else:
    # Fallback if last target onset wasn't found
    print("Warning: Could not determine last trial onset time for precise final wait calculation.")
    expected_end_of_last_trial_plus_rest = exp.clock.time - start_time # Use current time as best guess for end of activity+rest

# Calculate how much of the FINAL_WAIT is actually needed *after* the last trial's rest period
current_time_after_last_trial = exp.clock.time - start_time
# The target end time for the whole experiment is the end of the last trial's rest + the final wait buffer
target_experiment_end_time = expected_end_of_last_trial_plus_rest + FINAL_WAIT
required_final_wait = target_experiment_end_time - current_time_after_last_trial

if required_final_wait < 0:
    print(f"Warning: Experiment overran total expected time. Setting final wait to 0.")
    required_final_wait = 0

# Wait for the calculated final duration, checking for escape
wait_end_time = exp.clock.time + required_final_wait
while exp.clock.time < wait_end_time:
    if exp.keyboard.check(ESCAPE_KEY):
        # Ensure data is saved even if aborted during final wait
        # Corrected path concatenation for saving data on abort
        data_file = io.DataFile(filename=log_filename)
        data_file.add(exp.data)
        data_file.save() # Explicitly save
        control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
        sys.exit()
    exp.clock.wait(1) # Wait 1ms to yield CPU

# End Experiment
control.end(goodbye_text="", goodbye_delay=0)
