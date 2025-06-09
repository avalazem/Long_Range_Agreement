#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# =============================================================================
# French stimuli constructor (french local-global) 
# =============================================================================
'''

# =============================================================================
# MODULES AND GLOBALS
# =============================================================================
# modules
import os
import pandas as pd
import random
import numpy as np
import stim_utils as s
import warnings
import shutil
warnings.filterwarnings("ignore")

# alliases
join = os.path.join
make = os.makedirs
exists = os.path.exists
see = os.listdir
read = pd.read_csv

# =============================================================================
# NUMBER OF SUBJECTS & RUNS/BLOCKS
# =============================================================================
n_subjects = 1
n_runs = 6 # Total number of runs
n_blocks_per_run = 2 # Each run contains 2 blocks
# Total blocks = n_runs * n_blocks_per_run = 6

# =============================================================================
# NUMBER OF TRIALS (must be even numbers)
# =============================================================================
# Original calculation was per single-modality block.
# Now, each block has half visual, half auditory.
# We need half the number of trials per modality within each new block.

n_minimal_cell_reps = 2
# Original trials per structure (e.g., PP) per original block
original_structure_trials = 8 * n_minimal_cell_reps
# Trials per structure (e.g., PP) per modality in the new mixed block
structure_trials_per_modality = original_structure_trials // 2 # Half visual, half auditory

# Trials per condition (e.g., GSLS/PP) per modality in the new mixed block
trials_per_condition_per_modality = structure_trials_per_modality // 4

# Trials per grammatical number (e.g., GSLS/PP/sing) per modality in the new mixed block
trials_per_gr_number_per_modality = trials_per_condition_per_modality // 2

# Original filler trials per original block
original_filler_trials = original_structure_trials // 8
# Filler trials per modality in the new mixed block
filler_trials_per_modality = original_filler_trials // 2


# =============================================================================
# Assign Jitterd Rest Time
# =============================================================================
# Remember ali that num trials = original_filler trials
avg_time = 6 # seconds

def assign_jitter_durations(num_trials, num_rest_durations, mean_soa, step = 0.5):

    if num_trials % num_rest_durations != 0:
        print(f"Warning: Number of trials ({num_trials}) is not perfectly divisible by the number of rest durations ({num_rest_durations}). Rest times might not be perfectly balanced.")
    # Create full list of Rest Durations
    rest_durations = [mean_soa + step * (i - (num_rest_durations - 1) / 2) for i in range(num_rest_durations)]
    base_repeats = num_trials // num_rest_durations
    remainder = num_trials % num_rest_durations
    assigned_durations = rest_durations * base_repeats + [mean_soa] * remainder
    assert np.isclose(sum(assigned_durations), num_trials * mean_soa, atol=1e-6), "Sum of durations does not match the total required duration"
    return assigned_durations

    
        
    num_repeats = num_trials // num_rest_durations
    remainder = num_trials % num_rest_durations
    rest_durations_list = num_rest_durations * num_repeats + num_rest_durations[:remainder]
    random.shuffle(rest_durations_list) # Shuffle the rest for random presentation order
    # -----------------------------






# =============================================================================
# LOAD THE LEXICON
# =============================================================================
lexicon = s.load_lexicon()


def store_stimuli(stimuli, run_number, subject):
    if subject < 10:
        subject_str = '0'+str(subject)
    else:
        subject_str = str(subject)

    # Path structure: Stimuli/subject_XX/run_Y/
    path2run = join(os.path.realpath('../..'), 'Stimuli',
                    f'subject_{subject_str}', f'run_{run_number}')
    if not exists(path2run):
        make(path2run)
    # Filename: sub_X_run_Y.csv (modality is mixed within the block)
    fname = join(path2run, f'sub_{subject_str}_run_{run_number}.csv')
    stimuli.to_csv(fname, index=False) # Added index=False for cleaner CSV


def make_stimuli(lexicon):
    # =========================================================================
    # MAKE VISUAL STIMULI FOR THIS BLOCK
    # =========================================================================
    lr_pp_df_vis = s.make_lr_pp_stimuli(trials_per_gr_number_per_modality, lexicon, 'visual')
    sr_pp_df_vis = s.make_sr_pp_stimuli(trials_per_gr_number_per_modality, lexicon, 'visual')
    obj_df_vis = s.make_obj_stimuli(trials_per_gr_number_per_modality, lexicon, 'visual')
    # Fillers (optional, uncomment if needed)
    # pp_fillers_df_vis = s.make_pp_fillers(filler_trials_per_modality, lexicon, 'visual')
    # obj_fillers_df_vis = s.make_obj_fillers(filler_trials_per_modality, lexicon, 'visual')

    stimuli_vis = pd.concat([lr_pp_df_vis, obj_df_vis, sr_pp_df_vis]) # Add fillers here if needed
    stimuli_vis['modality'] = 'visual'
    stimuli_vis = stimuli_vis.sample(frac=1).reset_index(drop=True) # Shuffle visual stimuli

    # =========================================================================
    # MAKE AUDITORY STIMULI FOR THIS BLOCK
    # =========================================================================
    lr_pp_df_aud = s.make_lr_pp_stimuli(trials_per_gr_number_per_modality, lexicon, 'auditory')
    sr_pp_df_aud = s.make_sr_pp_stimuli(trials_per_gr_number_per_modality, lexicon, 'auditory')
    obj_df_aud = s.make_obj_stimuli(trials_per_gr_number_per_modality, lexicon, 'auditory')
    # Fillers (optional, uncomment if needed)
    # pp_fillers_df_aud = s.make_pp_fillers(filler_trials_per_modality, lexicon, 'auditory')
    # obj_fillers_df_aud = s.make_obj_fillers(filler_trials_per_modality, lexicon, 'auditory')

    stimuli_aud = pd.concat([lr_pp_df_aud, obj_df_aud, sr_pp_df_aud]) # Add fillers here if needed
    stimuli_aud['modality'] = 'auditory'
    stimuli_aud = stimuli_aud.sample(frac=1).reset_index(drop=True) # Shuffle auditory stimuli

    # =========================================================================
    # COMBINE AND SHUFFLE
    # =========================================================================
    if random.choice([True, False]):
        stimuli = pd.concat([stimuli_vis, stimuli_aud]).reset_index(drop=True) # Reset index after concat
    else:
        stimuli = pd.concat([stimuli_aud, stimuli_vis]).reset_index(drop=True) # Reset index after concat

    # Add Trial column (1-based)
    stimuli['trial'] = [f'trial_{i+1}' for i in range(len(stimuli))]

    # Reorder columns to put 'trial' first
    cols = ['trial'] + [col for col in stimuli.columns if col != 'trial']
    stimuli = stimuli[cols]
    stimuli['rest_duration'] = assign_jitter_durations(len(stimuli), num_rest_durations = 5, mean_soa = avg_time, step = 0.5)
    return stimuli

#%%
# =============================================================================
# WRAP UP
# =============================================================================
print('', 40*'--', '\n', 'Generating the Stimuli.', '\n', 40*'--')
path2stim_base = join(os.path.realpath('../..'), 'Stimuli')
if exists(path2stim_base):
    print(f'Removing existing stimuli directory: {path2stim_base}')
    shutil.rmtree(path2stim_base)
make(path2stim_base) # Recreate base directory


for subject in range(1, n_subjects+1):
    print(f'Generating stimuli for Subject {subject}...')
    for run_number in range(1, n_runs+1):
        print(f'  Run {run_number}...')
        # make stimuli for this run (mixed modality)
        stimuli = make_stimuli(lexicon)
        # store
        store_stimuli(stimuli, run_number, subject)
    print(f'Finished Subject {subject}.')
    
print('', 40*'--', '\n', 'Stimuli generation complete.', '\n', 40*'--')
