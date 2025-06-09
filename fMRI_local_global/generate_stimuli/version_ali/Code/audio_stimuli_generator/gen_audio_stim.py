#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 13:24:59 2021

@author: czacharo
"""
# =============================================================================
# IMPORT MODULES
# =============================================================================
import os
import pandas as pd
from google.cloud import texttospeech
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
import random # Add random import
import glob # Add glob import
# =============================================================================
# ADDD CREDENTIALS

# =============================================================================
class APIKeyCredentials(Credentials):
    def __init__(self, api_key):
        super().__init__()
        self._api_key = api_key

    def refresh(self, request):
        pass

    def apply(self, headers, token=None):
        headers['x-goog-api-key'] = self._api_key

# Set API key
api_key = "API_KEY"

# Create credentials from the API key
credentials = APIKeyCredentials(api_key)

# Instantiates a client with the API key
client = texttospeech.TextToSpeechClient(credentials=credentials)


# =============================================================================
# LOAD STIMULI
# =============================================================================
def get_subjects():
    path2stimuli = os.path.realpath('../../Stimuli')
    # Filter out non-directory items like .DS_Store
    subjects = [d for d in os.listdir(path2stimuli) if os.path.isdir(os.path.join(path2stimuli, d))]
    return subjects


def get_stim_files(subject):
    """Gets all stimulus CSV file paths for a given subject."""
    path2stimuli = os.path.realpath('../../Stimuli')
    subject_path = os.path.join(path2stimuli, subject)
    # Find CSV files in both auditory and visual subdirectories, or any other subdirectory
    stim_files = glob.glob(os.path.join(subject_path, '**/*.csv'), recursive=True)
    # Sort files to maintain a consistent order (e.g., run_1, run_2, ...)
    stim_files.sort()
    return stim_files

# =============================================================================
# ADD COMMAS TO THE SENTENCES
# =============================================================================


def add_comma(sentences, structures):
    collector = []
    for sentence, structure in zip(sentences, structures):
        splitted_sentence = sentence.split(' ')
        if structure == 'lr_pp':
            splitted_sentence[1] = splitted_sentence[1]+','
            splitted_sentence[-4] = splitted_sentence[-4]+','
            collector.append(' '.join(splitted_sentence))
            
        elif structure == 'sr_pp':
            splitted_sentence[-6] = splitted_sentence[-6]+','
            collector.append(' '.join(splitted_sentence))

        elif structure == 'lr_obj':
            splitted_sentence[1] = splitted_sentence[1]+','
            splitted_sentence[-3] = splitted_sentence[-3]+','
            collector.append(' '.join(splitted_sentence))

    # return the new sentences that now include commas
    return collector

# =============================================================================
# GET SENTENCES
# =============================================================================


def split_df(curr_block):
    # Check if 'Unnamed: 0' exists and rename it to avoid potential conflicts
    # or if it's simply an unwanted index column from saving previously.
    if 'Unnamed: 0' in curr_block.columns:
        # Option 1: Drop it if it's just the old index
        # curr_block = curr_block.drop(columns=['Unnamed: 0'])
        # Option 2: Rename it if it contains useful info (less likely here)
        curr_block = curr_block.rename(columns={'Unnamed: 0': 'original_index'})

    # Create a numerical trial column based on the DataFrame's 0-based index + 1
    # This ensures trials start from 1.
    curr_block['trial_num'] = curr_block.index + 1

    # Get the numerical trial numbers as a list
    trial_numbers = curr_block['trial_num'].tolist()

    # Create the formatted trial strings (e.g., 'trial_1', 'trial_2')
    trials = [f'trial_{num}' for num in trial_numbers]

    # Assign the formatted strings to the final 'trial' column
    # This uses the recommended bracket notation for column assignment.
    curr_block['trial'] = trials

    # Extract sentences, structures, and probe words, checking if columns exist
    sentences = curr_block['sentence'].tolist() if 'sentence' in curr_block.columns else []
    structures = curr_block['structure'].tolist() if 'structure' in curr_block.columns else []
    probe_words = curr_block['probe_word'].tolist() if 'probe_word' in curr_block.columns else [] # Added probe_word extraction

    # Return the list of trial strings, sentences, the modified DataFrame, structures, and probe words
    return trials, sentences, curr_block, structures, probe_words # Added probe_words to return


# =============================================================================
# SYNTHETIZE AUDIO FROM TEXT
# =============================================================================

def text_to_wav(voice_name, params, text):

    language_code = "-".join(voice_name.split("-")[:2])
    text_input = texttospeech.SynthesisInput(text=text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        pitch=params['pitch'],
        speaking_rate=params['speaking_rate'],
        sample_rate_hertz=44100,

    )
    #client = texttospeech.TextToSpeechClient() # removed since using key directly
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config
    )

    return response


def store_wav(response, trial, sentence, path2block):

    # make dirs
    wav_dir = os.path.join(path2block, 'wavs')
    if not os.path.exists(wav_dir):
        os.makedirs(wav_dir)

    sentence_dir = os.path.join(path2block, 'sentences')
    if not os.path.exists(sentence_dir):
        os.makedirs(sentence_dir)

    # Store the .wav files
    wav_filename = os.path.join(wav_dir, f"{trial}.wav")
    with open(wav_filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to "{wav_filename}"')

    # store the sentence as a .txt
    txt_filename = os.path.join(sentence_dir, f"{trial}.txt")
    with open(txt_filename, "w") as text_file:
        text_file.write(sentence)


def store_probe_wav(response, trial, path2block):
    """Stores the probe word .wav file."""
    wav_dir = os.path.join(path2block, 'wavs')
    # Ensure wav_dir exists (might be created by store_wav already, but check again)
    if not os.path.exists(wav_dir):
        os.makedirs(wav_dir)

    # Store the .wav file for the probe word
    wav_filename = os.path.join(wav_dir, f"{trial}_probe.wav")
    with open(wav_filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Probe audio content written to "{wav_filename}"')


def make_block_dir(block_name, subject):
    """Creates the output directory for a specific run/block for a subject."""
    # send them directly to the run_experiment folder
    path2exp = os.path.realpath(
        '../../../../run_experiment/version_ali_2/Stimuli/')
    # Output generated files directly into the subject's run folder
    path2block = os.path.join(path2exp, f'{subject}',
                              block_name) # Removed 'auditory' subfolder
    if not os.path.exists(path2block):
        os.makedirs(path2block)

    return path2block

# %%
# =============================================================================
# WRAP UP
# =============================================================================
# load stimuli
male_voice = "fr-FR-Wavenet-G"  # french Male: "fr-FR-Wavenet-G"
female_voice = "fr-FR-Wavenet-C"  # french Female: "fr-FR-Wavenet-C"
params = {}
params['pitch'] = 1.2
params['speaking_rate'] = 0.93


subjects = get_subjects()
for subject in subjects:
    print(f"Processing subject: {subject}")
    stim_files = get_stim_files(subject)

    if not stim_files:
        print(f"  No stimulus files found for subject {subject}. Skipping.")
        continue

    # Process all stimulus files found for the subject
    for stim_filepath in stim_files:
        try:
            # Extract block name from filename (e.g., "run_1" from ".../visual/run_1.csv")
            block_name = os.path.splitext(os.path.basename(stim_filepath))[0]
            print(f"  Processing block: {block_name}")

            # Load the current block's data
            curr_block = pd.read_csv(stim_filepath, sep=',')

            # --- Filter for Auditory Trials Only ---
            if 'modality' not in curr_block.columns:
                print(f"    Warning: 'modality' column not found in {block_name}. Skipping audio generation for this file.")
                continue # Skip to the next file
            # Ensure 'probe_word' column exists for auditory trials before proceeding
            if 'probe_word' not in curr_block.columns:
                 print(f"    Warning: 'probe_word' column not found in {block_name}. Skipping probe audio generation for this file.")
                 # Decide if you want to continue generating sentence audio or skip entirely
                 # continue # Option: skip this file entirely if probe_word is missing

            auditory_trials_df = curr_block[curr_block['modality'].str.lower() == 'auditory'].copy()
            if auditory_trials_df.empty:
                print(f"    No auditory trials found in {block_name}. Skipping audio generation.")
                # Still save the original CSV even if no audio is generated
                path2block = make_block_dir(block_name, subject)
                output_csv_fname = os.path.join(path2block, block_name + '.csv')
                curr_block.to_csv(output_csv_fname, index=False)
                print(f"    Original CSV saved to {output_csv_fname}")
                continue # Skip to the next file
            # -----------------------------------------

            # Create the output directory using the new structure
            path2block = make_block_dir(block_name, subject) # Use the renamed function

            # --- Audio Generation (for auditory trials only) ---
            # Split the *filtered* dataframe to get sentences, etc. for auditory trials
            # Make sure probe_words are extracted
            trials, sentences, _, structures, probe_words = split_df(auditory_trials_df) # Use the filtered df

            # Check if probe_words list has the same length as trials (important if 'probe_word' column was missing)
            if len(probe_words) != len(trials):
                 print(f"    Warning: Mismatch between number of trials and probe words in {block_name}. Skipping probe audio generation.")
                 # Set probe_words to None or handle appropriately to avoid errors later
                 probe_words = [None] * len(trials) # Example: Fill with None

            # Add commas for better TTS parsing
            sentences_with_commas = add_comma(sentences, structures)

            # Determine number of *auditory* trials and assign voices randomly
            n_trials = len(trials) # Number of auditory trials
            if n_trials > 0:
                n_male = n_trials // 2
                n_female = n_trials - n_male
                voices_for_block = [male_voice] * n_male + [female_voice] * n_female
                random.shuffle(voices_for_block) # Shuffle voices for random assignment

                # Generate and store .wavs and .txts for each *auditory* trial with assigned voice
                for i, (trial, sentence, voice) in enumerate(zip(trials, sentences_with_commas, voices_for_block)):
                    # --- Sentence Audio ---
                    # Create .wav with the assigned voice
                    response = text_to_wav(voice, params, sentence)
                    # Store the .wav and .txt files
                    store_wav(response, trial, sentence, path2block)

                    # --- Probe Word Audio ---
                    current_probe_word = probe_words[i] if probe_words[i] is not None else None

                    if current_probe_word: # Only generate if probe word exists for this trial
                        # Determine the opposite voice for the probe
                        if voice == male_voice:
                            probe_voice = female_voice
                        else:
                            probe_voice = male_voice

                        # Synthesize the probe word audio
                        probe_response = text_to_wav(probe_voice, params, current_probe_word)

                        # Store the probe word .wav file
                        store_probe_wav(probe_response, trial, path2block)
                    else:
                        print(f"    Skipping probe audio for {trial} due to missing probe word.")


            # --- Store Original CSV ---
            # Store the block's original .csv in the output directory
            output_csv_fname = os.path.join(path2block, block_name + '.csv')
            # Use the original curr_block DataFrame loaded from the file
            curr_block.to_csv(output_csv_fname, index=False) # Save without pandas index
            print(f"    Original CSV saved to {output_csv_fname}")

        except Exception as e:
            print(f"  Error processing file {stim_filepath}: {e}")