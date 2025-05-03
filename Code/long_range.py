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
from expyriment import design, control, stimuli, misc, io, stimuli

script_dir = Path(__file__).parent.resolve()

# Experiment Parameters
DEBUG = False  # Set to False for fullscreen, True for development mode
INITIAL_WAIT = 2000  # ms, Wait time after instructions before first trigger/trial
FINAL_WAIT = 10000   # ms, Wait time at the end of the experiment
TEXT_SIZE = 50
TEXT_FONT =  str(script_dir / 'Arial.ttf')  # Font for sentence presentation
PROBE_SIZE = 70
PROBE_FONT = str(script_dir / 'Times_New_Roman_Bold.ttf') # Font for probe presentation
LEFT_HAND_KEY =  misc.constants.K_y # Key to press after sentence presentation for FALSE (Use constant)
RIGHT_HAND_KEY = misc.constants.K_f # "                                      " for TRUE  (Use constant)
TRIGGER_KEY = misc.constants.K_t# fMRI trigger key
NUM_TRIGGERS = 3 # Number of triggers to wait for
ESCAPE_KEY = misc.constants.K_ESCAPE # Key to exit the experiment
CONTROLLER_KEY = misc.constants.K_SPACE # Key for experimenter to start after instructions

# Timing Parameters (modify as needed)
STIMULUS_ONTIME = 250           # ms, Duration each word is shown (visual) (like params.stimulus_ontime)
STIMULUS_ITI = 250              # ms, Duration of the inter-stimulus interval (like params.stimulus_iti)
SOA_PROBE = 1000               # ms, Fixation duration AFTER sentence BEFORE probe for both modalities (added to last ITI for integer reasons...)
PROBE_DURATION = 1500           # ms, Duration of the probe (based on 'Neural Populations' paper)
KEY_WAIT_DURATION = PROBE_DURATION # ms, Currently waits for key press only during probe presentation but can tweak this by defining this 
AUDIO_DURATION = 4000           # ms, Duration of the audio stimulus (like params.audio_duration)
REST_DURATIONS = [4500, 5000, 5500, 6000, 6500] # ms, Base rest durations to choose from (average is 6000)
# ----------------------------------------

# Check for correct usage
if len(sys.argv) != 2:
    print("""Usage: python long_range.py <run_folder_path>

Arguments:
    run_folder_path: Path to the directory containing the stimulus CSV file and .wav audio files.
                       (e.g., ../Stimuli/subject_01/visual/sub1_run1_visual)
""")
    sys.exit(1)

run_folder_path = Path(sys.argv[1]).resolve() # Resolve to absolute path

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

# --- Load Stimuli CSV EARLY to determine modality ---
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
    project_root = run_folder_path.parents[3] # /home/avalazem/Desktop/Work/Single_Word_Processing_Stage/Long_Range_Agreement/Long_Range_Pilot
    log_dir = project_root / "Logs"
    log_dir.mkdir(exist_ok=True) # Ensure log directory exists

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

# --- Generate Jittered Rest Times ---
num_trials = len(stim_df)
num_rest_durations = len(REST_DURATIONS)
if num_trials % num_rest_durations != 0:
    print(f"Warning: Number of trials ({num_trials}) is not perfectly divisible by the number of rest durations ({num_rest_durations}). Rest times might not be perfectly balanced.")
# Create full list of Rest Durations
num_repeats = num_trials // num_rest_durations
remainder = num_trials % num_rest_durations
rest_durations_list = REST_DURATIONS * num_repeats + REST_DURATIONS[:remainder]
import random
random.shuffle(rest_durations_list) # Shuffle the rest for random presentation order
# -----------------------------

# --- Expyriment Setup ---
exp = design.Experiment(name=f"Long-Range Agreement - Sub {subject_id} Run {run_number})", text_size=TEXT_SIZE)
control.defaults.initialize_delay = 0 # Avoids initial pause screen
if DEBUG:
    control.set_develop_mode(on=True, window_size=(800, 600))
control.initialize(exp)

# --- Prepare Stimuli Objects ---
fixation_cross = stimuli.FixCross(size=(50, 50), line_width=4)
blank_screen = stimuli.BlankScreen()
instruction_text = f"Vous allez voir ou entendre des phrases.\n\nAprès chaque phrase, lorsque un mot s'affiche, appuyez sur le bouton droit s'il était dans la phrase, sur le bouton gauche sinon.\n\nRestez immobile et attentif.\n\nAppuyez sur la barre d'espace pour commencer..."
ready_text = "Attendez..."
end_text = f"Fin de cette partie. Merci!"

# --- Preload Static Stimuli ---
fixation_cross.preload()
blank_screen.preload()
# Preload instruction/feedback text screens
stimuli.TextScreen("Instructions", instruction_text).preload()
stimuli.TextLine(ready_text).preload()
stimuli.TextScreen("Fin", end_text).preload()


# --- Preload Trial Stimuli ---
preloaded_stimuli = {} # Dictionary to hold preloaded stimuli for each trial
preloaded_word_counts = {} # Dictionary to hold word counts for visual trials

for index, trial_data in stim_df.iterrows():
    # Use 1-based index for trial ID and filename, matching row number
    trial_id_one_based = index + 1
    sentence = trial_data['sentence']
    current_modality = trial_data['modality'].lower() # Get modality for this specific trial

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
        # Ensure the 'trial' column exists before accessing it
        if 'trial' not in trial_data:
            print(f"Error: 'trial' column missing in input CSV for row index {index}. Cannot determine audio filename.")
            preloaded_stimuli[trial_id_one_based] = None
            preloaded_word_counts[trial_id_one_based] = 0
            continue # Skip to next iteration

        trial_identifier = trial_data['trial'] # Get value like 'trial_1'
        wav_filename = f"{trial_identifier}.wav" # Construct filename directly
        # ----------------------------------------------------

        # Look for audio files in an 'wavs' subfolder of the run folder
        wav_path = stimuli_base_dir / "wavs" / wav_filename # Ensure this matches your folder name ('audio' or 'wavs')
        if wav_path.is_file():
            try:
                audio_stim = stimuli.Audio(str(wav_path))
                audio_stim.preload()
                preloaded_stimuli[trial_id_one_based] = audio_stim # Use 1-based index as key (dictionary key remains the same for now)
            except Exception as e:
                print(f"Warning: Could not preload audio file {wav_path}: {e}")
                preloaded_stimuli[trial_id_one_based] = None # Mark as failed preload
        else:
            print(f"Warning: Audio file not found during preload for trial {trial_id_one_based}: {wav_path}")
            preloaded_stimuli[trial_id_one_based] = None # Mark as not found
        preloaded_word_counts[trial_id_one_based] = 0 # Store 0 for auditory trials

# --- Calculate Expected Trial Timings and Total Duration ---
expected_total_duration = INITIAL_WAIT
target_onset_times = {}
current_target_onset = INITIAL_WAIT # Start after initial wait

for index, trial_data in stim_df.iterrows():
    trial_id_one_based = index + 1
    target_onset_times[trial_id_one_based] = current_target_onset # Store expected onset for this trial

    current_modality = trial_data['modality'].lower()
    word_count = preloaded_word_counts.get(trial_id_one_based, 0)
    current_iti = rest_durations_list[index]

    # Calculate the duration of the stimulus presentation + probe + response window
    if current_modality == 'visual':
        # Visual: Sum of word times, IWIs, SOA, probe, key wait
        trial_stim_probe_duration = (word_count * STIMULUS_ONTIME) + (word_count * STIMULUS_ITI) + SOA_PROBE + PROBE_DURATION 
    elif current_modality == 'auditory':
        # Auditory: Fixed audio time, SOA, probe, key wait
        trial_stim_probe_duration = AUDIO_DURATION + SOA_PROBE + PROBE_DURATION
    else:
        trial_stim_probe_duration = 0 # Should not happen

    # Add this trial's duration and its ITI to find the start of the *next* trial
    current_target_onset += trial_stim_probe_duration + current_iti

# The final target onset time represents the start of the final wait
expected_total_duration = current_target_onset + FINAL_WAIT

print(f"Total number of trials: {num_trials}")
print(f"Expected Total duration: {expected_total_duration / 1000.0:.2f} s")

# --- Experiment Flow ---
control.start(skip_ready_screen=True)

# Display instructions
stimuli.TextScreen("Instructions", instruction_text).present()
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
exp.data_variable_names = ["TrialNumber", "Sentence", "Structure", "Modality", "KEY", "RT_ms"]

# --- Main Trial Loop ---
print("Starting main trial loop...") # Added for clarity

for index, trial_data in stim_df.iterrows():
    sentence = trial_data['sentence']
    structure = trial_data['structure']
    current_modality = trial_data['modality'].lower()
    probe_word = trial_data['probe_word'].upper() # <-- Get probe word and convert to uppercase to differentiate low-level perceptions
    # Use 1-based index for trial number identification and logging
    trial_id_one_based = index + 1 # This is the CURRENT trial number in the loop

    # --- Wait until the target onset time for this trial --- (Added)
    target_onset = target_onset_times.get(trial_id_one_based, -1)
    if target_onset > 0:
        while exp.clock.time - start_time < target_onset:
            # Actively wait (yields processing time)
            exp.keyboard.check(process_control_events=True) # Check for escape key etc.
            pass # Keep looping until target time is reached
    # -------------------------------------------------------

    # --- Timing Verification (Print AFTER waiting) ---
    actual_onset = exp.clock.time - start_time # Get current time relative to start
    delta = actual_onset - target_onset
    warn = " !!!" if delta > 500 else ""
    # Print timing info for the *current* trial (moved back here, prints after the wait)
    print(f"Trial {trial_id_one_based}: Target: {target_onset:.2f} Actual: {actual_onset:.2f} Delta: {delta:.2f}{warn}")
    # ---------------------------------------------

    # Retrieve preloaded stimulus using the 1-based index
    current_stim = preloaded_stimuli.get(trial_id_one_based)

    # Skip trial if stimulus failed to load/preload
    if current_stim is None:
         print(f"Skipping trial {trial_id_one_based} due to missing/failed stimulus.")
         # Log using 1-based trial number
         exp.data.add([trial_id_one_based, sentence, structure, current_modality, -3])
         continue

    # 1. Stimulus Presentation
    stimulus_start_time = exp.clock.time
    stimulus_end_time = 0
    if current_modality == 'visual':
        visual_stim_list = current_stim
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

    elif current_modality == 'auditory':
        audio_stim = current_stim
        try:
            fixation_cross.present() # Keep fixation during audio
            audio_filename_to_play = getattr(audio_stim, 'filename', 'N/A')
            audio_play_start_time = exp.clock.time
            audio_stim.play() # Start playing audio (non-blocking)

            # Wait for AUDIO_DURATION, checking for escape periodically
            wait_end_time = exp.clock.time + AUDIO_DURATION
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    audio_stim.stop()
                    control.end(goodbye_text="Experiment aborted.", goodbye_delay=1000)
                    sys.exit()
                # Wait for a short interval before checking again
                exp.clock.wait(10) # Check every 10ms

            # Ensure the loop finishes close to the target time, handle potential overshoot
            remaining_wait = wait_end_time - exp.clock.time
            if remaining_wait > 0:
                exp.clock.wait(remaining_wait)

            audio_stim.stop() # Stop playback immediately after AUDIO_DURATION
            stimulus_end_time = exp.clock.time # End time is right after audio stops
        except Exception as e:
            print(f"Error presenting preloaded audio for trial {trial_id_one_based}: {e}")
            # Log using 1-based trial number
            exp.data.add([trial_id_one_based, sentence, structure, current_modality, -2])
            # Go directly to Rest duration for this trial
            blank_screen.present()
            current_rest = rest_durations_list[index] # Rest still uses 0-based index
            exp.clock.wait(current_rest)
            continue # Skip rest of trial logic

    # 2. Post-Stimulus Fixation (SOA_PROBE)
    fixation_cross.present()
    exp.clock.wait(SOA_PROBE)
    post_stim_fixation_end_time = exp.clock.time

    # 3. Probe Presentation & Response Window (Combined)
    # Create probe stimulus dynamically for the current trial
    current_probe = stimuli.TextLine(probe_word, text_size=PROBE_SIZE, text_font=PROBE_FONT)
    current_probe.present() # <-- Present the trial-specific probe
    prompt_onset_time = exp.clock.time

    # Wait for key press DURING probe presentation

    # Use the constants in the wait call
    keys, rt = exp.keyboard.wait(keys=[LEFT_HAND_KEY, RIGHT_HAND_KEY, ESCAPE_KEY], duration=PROBE_DURATION, process_control_events=True)

    # --- Check for Escape Key during probe wait ---
    if keys == ESCAPE_KEY:
        control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
        sys.exit()
    # ---------------------------------------------

    # --- Ensure full duration wait even if key pressed early ---
    if rt is not None: # Key was pressed before timeout
        remaining_wait = PROBE_DURATION - rt
        if remaining_wait > 0:
            exp.clock.wait(remaining_wait) # Wait for the remainder of the duration
    # If rt is None, the full duration already passed.
    # ---------------------------------------------------------

    # RT is relative to the start of the wait (prompt_onset_time)
    logged_rt = rt if rt is not None else -999 # Use -999 for timeout

    # Convert key code to string manually based on the constants used
    if keys == LEFT_HAND_KEY:
        logged_key = 'left (FALSE)'
    elif keys == RIGHT_HAND_KEY:
        logged_key = 'right (TRUE)' 
    else: # keys is None (timeout)
        logged_key = "TIMEOUT"

    # The wait is finished, the probe implicitly disappears when the next stimulus (ITI fixation) is presented.
    response_window_actual_end_time = exp.clock.time # Mark the end of the combined window

    # 4. Log Data (\n    # Log using 1-based trial number
    exp.data.add([trial_id_one_based, sentence, structure, current_modality, logged_key, logged_rt]) # Log the string representation

    # 5. Inter-Trial Interval (ITI) - Dynamic Wait Calculation
    fixation_cross.present() # Present fixation for ITI

    # Calculate the target onset for the *next* trial
    next_trial_index = index + 1
    if next_trial_index < num_trials:
        # Target onset for the next trial (trial_id_one_based + 1)
        target_onset_next_trial = target_onset_times.get(trial_id_one_based + 1, -1)
        if target_onset_next_trial > 0:
            current_time_before_iti_wait = exp.clock.time - start_time
            required_iti_wait = target_onset_next_trial - current_time_before_iti_wait

            # Ensure wait time is not negative (safety check)
            if required_iti_wait < 0:
                print(f"Warning: Trial {trial_id_one_based} overran expected end time. Setting ITI wait to 0.")
                required_iti_wait = 0

            # Wait exactly the time needed, checking for escape
            wait_end_time = exp.clock.time + required_iti_wait
            while exp.clock.time < wait_end_time:
                if exp.keyboard.check(ESCAPE_KEY):
                    control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
                    sys.exit()
                exp.clock.wait(1) # Wait 1ms to yield CPU

            # exp.clock.wait(required_iti_wait) # Wait exactly the time needed <-- Replaced by loop above
        else:
             print(f"Warning: Could not get target onset for next trial {trial_id_one_based + 1}. Using default ITI.")
             # Fallback to a default ITI if next target onset is missing (shouldn't happen)
             default_iti = 3000 # Or use rest_durations_list[index] as a fallback
             # exp.clock.wait(default_iti) <-- Replace this too if needed, or keep simple wait for fallback
             wait_end_time = exp.clock.time + default_iti
             while exp.clock.time < wait_end_time:
                 if exp.keyboard.check(ESCAPE_KEY):
                     control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
                     sys.exit()
                 exp.clock.wait(1)
    else:
        # This was the last trial, the final wait is handled after the loop
        pass

# --- End of Main Trial Loop ---

# --- End of Experiment ---
stimuli.TextScreen("Fin", end_text).present()

# Calculate the expected end time of the last trial's activity
last_trial_target_onset = target_onset_times.get(num_trials, -1)
if last_trial_target_onset > 0:
    last_trial_data = stim_df.iloc[-1]
    last_modality = last_trial_data['modality'].lower()
    last_word_count = preloaded_word_counts.get(num_trials, 0)

    if last_modality == 'visual':
        last_trial_stim_probe_duration = (last_word_count * STIMULUS_ONTIME) + (last_word_count * STIMULUS_ITI) + SOA_PROBE + PROBE_DURATION
    elif last_modality == 'auditory':
         last_trial_stim_probe_duration = AUDIO_DURATION + SOA_PROBE + PROBE_DURATION
    else:
        last_trial_stim_probe_duration = 0

    expected_end_of_last_trial_activity = last_trial_target_onset + last_trial_stim_probe_duration
else:
    # Fallback if last target onset wasn't found
    expected_end_of_last_trial_activity = exp.clock.time - start_time # Use current time as best guess

# Calculate how much of the FINAL_WAIT is actually needed
current_time_after_last_trial = exp.clock.time - start_time
required_final_wait = (expected_end_of_last_trial_activity + FINAL_WAIT) - current_time_after_last_trial

if required_final_wait < 0:
    print(f"Warning: Experiment overran total expected time. Setting final wait to 0.")
    required_final_wait = 0

# Wait for the calculated final duration, checking for escape
wait_end_time = exp.clock.time + required_final_wait
while exp.clock.time < wait_end_time:
    if exp.keyboard.check(ESCAPE_KEY):
        control.end(goodbye_text="Experiment aborted by user.", goodbye_delay=1000)
        sys.exit()
    exp.clock.wait(1) # Wait 1ms to yield CPU

# exp.clock.wait(required_final_wait) # Wait for the calculated final duration <-- Replaced by loop above

control.end(goodbye_text="", goodbye_delay=0)
