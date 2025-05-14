import pandas as pd
import os
import random

def create_custom_localizer_csvs():
    # --- Configuration ---
    source_stim_folder = "/home/avalazem/Desktop/Work/Single_Word_Processing_Stage/Long_Range_Agreement/Christophe_Localizer/lang_localizer/stim"
    output_csv_folder = "/home/avalazem/Desktop/Work/Single_Word_Processing_Stage/Long_Range_Agreement/Christophe_Localizer/lang_localizer/long-range_stim"
    
    num_subjects_to_generate = 2
    subject_id_start = 1
    
    num_blocks = 16
    trials_per_block = 5
    initial_onset_ms = 1500
    inter_block_interval_ms = 8000 # Interval after a block's last trial, before next block's first trial

    # --- 1. Load and Process Initial Stimuli Data ---
    fname_sent_durations_initial = {}
    print(f"Scanning source CSVs in: {source_stim_folder}")
    try:
        if not os.path.isdir(source_stim_folder):
            print(f"Error: Source stimulus folder not found at {source_stim_folder}")
            return

        for filename in os.listdir(source_stim_folder):
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(source_stim_folder, filename)
                try:
                    df_temp = pd.read_csv(file_path)
                    if "fname" in df_temp.columns and "sent_dur" in df_temp.columns:
                        for _index, row in df_temp.iterrows():
                            fname = row["fname"]
                            sent_dur = row["sent_dur"]
                            if pd.notna(fname) and pd.notna(sent_dur):
                                if fname not in fname_sent_durations_initial:
                                    try:
                                        fname_sent_durations_initial[fname] = int(sent_dur)
                                    except ValueError:
                                        print(f"  Warning: Could not convert sent_dur \'{sent_dur}\' to int for fname \'{fname}\' in {filename}. Skipping.")
                                # No verification for differing durations here, just take the first.
                    else:
                        print(f"  Skipping {filename}: missing 'fname' or 'sent_dur' column.")
                except Exception as e:
                    print(f"  Error processing file {filename}: {e}")
    except Exception as e:
        print(f"Error listing source stimulus directory: {e}")
        return
        
    print(f"Initial unique fnames loaded: {len(fname_sent_durations_initial)}")

    # --- 2. Filter Stimuli ---
    fname_sent_durations_filtered = {
        fname: dur
        for fname, dur in fname_sent_durations_initial.items()
        if not fname.startswith("ch")
    }
    print(f"Fnames after removing 'ch' prefix: {len(fname_sent_durations_filtered)}")

    fr_stimuli_pool = []  # List of (fname, sent_dur)
    wol_stimuli_pool = [] # List of (fname, sent_dur)

    for fname, dur in fname_sent_durations_filtered.items():
        if fname.lower().startswith("fr_"):
            fr_stimuli_pool.append((fname, dur))
        elif fname.lower().startswith("wol"):
            wol_stimuli_pool.append((fname, dur))
            
    random.shuffle(fr_stimuli_pool) # Shuffle once initially
    random.shuffle(wol_stimuli_pool)
    
    print(f"French stimuli available: {len(fr_stimuli_pool)}")
    print(f"Wolof stimuli available: {len(wol_stimuli_pool)}")

    if not os.path.exists(output_csv_folder):
        os.makedirs(output_csv_folder)
        print(f"Created output directory: {output_csv_folder}")

    # --- 3. Generate New CSV Files ---
    # fr_needed_per_subject and wol_needed_per_subject are not strictly needed upfront
    # if we are sampling per block and allowing reuse across blocks.

    for s_offset in range(num_subjects_to_generate):
        subj_id = subject_id_start + s_offset
        all_trials_for_subject = []
        current_onset_tracker = initial_onset_ms # This will be the onset for the first trial
        
        print(f"\nGenerating CSV for Subject ID: {subj_id}")

        # Removed pre-creation of subject_fr_set and subject_wol_set
        # Stimuli will be selected on a per-block basis.

        for block_idx in range(num_blocks):
            is_fr_block = block_idx % 2 == 0
            lang_for_block = "fr" if is_fr_block else "wol"
            
            # print(f"  Block {block_idx} ({lang_for_block})")

            stimuli_for_this_block = []
            pool_to_use_for_block = fr_stimuli_pool if is_fr_block else wol_stimuli_pool

            if not pool_to_use_for_block:
                print(f"  FATAL ERROR: Stimulus pool for language '{lang_for_block}' is empty. Cannot generate block {block_idx} for Subject {subj_id}.")
                # This is a critical error; consider how to handle. Maybe skip subject or stop.
                # For now, if a pool is empty, subsequent blocks of this lang will also fail.
                break # Break from generating blocks for this subject if a language pool is empty

            if len(pool_to_use_for_block) < trials_per_block:
                print(f"  Warning: Stimulus pool for language '{lang_for_block}' ({len(pool_to_use_for_block)} items) is smaller than trials_per_block ({trials_per_block}). Duplicates within block {block_idx} for Subject {subj_id} are unavoidable.")
                # Sample with replacement if not enough unique stimuli for the block
                stimuli_for_this_block = random.choices(pool_to_use_for_block, k=trials_per_block)
            else:
                # Sample without replacement, ensuring unique stimuli within this block
                stimuli_for_this_block = random.sample(pool_to_use_for_block, trials_per_block)
            
            if len(stimuli_for_this_block) < trials_per_block:
                 print(f"    FATAL: Could not select enough stimuli for Subject {subj_id}, Block {block_idx}. Required {trials_per_block}, got {len(stimuli_for_this_block)}. Skipping rest of this subject's generation.")
                 # This indicates a problem even with random.choices or if pool_to_use_for_block was empty initially.
                 all_trials_for_subject = [] # Clear any partial data for this subject
                 break # Stop processing this subject

            for trial_in_block_idx, (selected_fname, selected_sent_dur) in enumerate(stimuli_for_this_block):
                global_trial_num = block_idx * trials_per_block + trial_in_block_idx + 1
                
                all_trials_for_subject.append({
                    "subj": subj_id,
                    "ntrial": global_trial_num,
                    "nbloc": block_idx,
                    "langue": lang_for_block,
                    "sent_dur": selected_sent_dur,
                    "fname": selected_fname,
                    "sent_onset": int(current_onset_tracker) # This is the onset for the current trial
                })

                # Update current_onset_tracker for the *next* trial:
                current_onset_tracker += selected_sent_dur # Add the duration of the current stimulus

                if trial_in_block_idx == trials_per_block - 1: # If this was the last trial in the block
                    # Add the inter-block interval
                    current_onset_tracker += inter_block_interval_ms
                else: # If not the last trial in the block
                    # Add the fixed intra-block ITI
                    current_onset_tracker += 1300
            
        if all_trials_for_subject: # Check if any trials were actually generated for this subject
            df_output = pd.DataFrame(all_trials_for_subject)
            output_filename = os.path.join(output_csv_folder, f"long-range_localizer_subj{subj_id}.csv")
            df_output.to_csv(output_filename, index=False)
            print(f"  Successfully generated: {output_filename}")
        else:
            print(f"  No trial data generated for Subject {subj_id}.")

if __name__ == "__main__":
    create_custom_localizer_csvs()
