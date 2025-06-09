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

# =============================================================================
# ADDD CREDENTIALS

# =============================================================================
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.getcwd(), 'key.json')


# =============================================================================
# LOAD STIMULI
# =============================================================================
def load_stim():
    path2stimuli = os.path.realpath('../../Stimuli/version_07/auditory')
    files = [os.path.join(path2stimuli, f) for f in os.listdir(path2stimuli)]
    files = [pd.read_csv(f, sep='\t') for f in files]

    return files


# =============================================================================
# ADD COMMAS TO THE SENTENCES
# =============================================================================
def add_comma(sentences, structures):
    collector=[]
    for sentence,structure  in zip(sentences, structures):
        splitted_sentence=sentence.split(' ') 
        splitted_sentence[1]= splitted_sentence[1]+','
        if structure =='pp':

           splitted_sentence[-3]= splitted_sentence[-3]+','
           collector.append(' '.join(splitted_sentence))
           
        elif structure=='obj':
           splitted_sentence[-2]= splitted_sentence[-2]+','
           collector.append(' '.join(splitted_sentence))        
        
    # return the new sentences that now include commas    
    return collector

# =============================================================================
# GET SENTENCES
# =============================================================================
def split_df(curr_block):
    curr_block = curr_block.rename(columns={'Unnamed: 0': 'trial'})
    curr_block.trial = curr_block.index.values+1

    trials = curr_block.trial.values.tolist()
    trials = [f'trial_{trial}' for trial in trials]
    curr_block['trial']=trials
    sentences = curr_block.sentence.values.tolist()
    structures= curr_block.structure.values.tolist()

    return trials, sentences, curr_block, structures


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
    client = texttospeech.TextToSpeechClient()
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


def create_auditory_trials(voice, params, sentences, 
                           trials, path2block, curr_block, block_name):
    for trial, sentence in zip(trials, sentences):
        # create .wav
        response = text_to_wav(voice, params, sentence)
        # store the .wav files
        store_wav(response, trial, sentence, path2block)

    # store the .csv also
    fname = os.path.join(path2block,block_name+'.csv')
    curr_block.to_csv(fname)


def make_dir(block_name):
    path2block = os.path.join(
        os.path.realpath('../../run_experiment/Stimuli/auditory'),
        block_name)
    if not os.path.exists(path2block):
        os.makedirs(path2block)

    return path2block


# =============================================================================
# WRAP UP
# =============================================================================
# load stimuli
voice = "en-US-Wavenet-F"  # french: "fr-FR-Wavenet-E"
params = {}
params['pitch'] = 1.2
params['speaking_rate'] = 0.93
block_names = ['LocalGlobal2', 'LocalGlobal4']

files = load_stim()
for block, block_name in zip(range(0, len(files)), block_names):
    # get path to block
    path2block = make_dir(block_name)
    # get the current block
    curr_block = files[block]
    # split the dataframe to store indivually the sentences and the .wav files
    trials, sentences, curr_block, structures = split_df(curr_block)
    # add commas to make the audio stimuli easier to parse
    sentences=add_comma(sentences, structures)
    
    # store .wavs and .txts
    create_auditory_trials(voice, params, sentences,
                           trials, path2block, curr_block, block_name)
