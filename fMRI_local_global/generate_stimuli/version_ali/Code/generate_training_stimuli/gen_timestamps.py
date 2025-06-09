#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 00:02:07 2021

@author: czacharo
"""

# =============================================================================
# IMPORT MODULES
# =============================================================================
import os
import io
import pandas as pd
import numpy as np
from google.cloud import speech
# =============================================================================
# ADDD CREDENTIALS
# =============================================================================
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.getcwd(), 'key.json')


# =============================================================================
# LOAD STIMULI
# =============================================================================

def load_stim(block_name):
    path2block = os.path.join(
        os.path.realpath('../../run_experiment/Stimuli/auditory'),
        block_name,'wavs')
    files=os.listdir(path2block)
    files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    wavs=[os.path.join(path2block,f) for f in files]
    trials=[f.split('.')[0] for f in files]

    return wavs, trials


def transcribe_file_with_word_time_offsets(speech_file, trial):
    """Transcribe the given audio file synchronously and output the word time
    offsets."""
    
    path2block = os.path.join(
        os.path.realpath('../../run_experiment/Stimuli/auditory'),
        block_name,'timestamps')
    if not os.path.exists(path2block):
        os.makedirs(path2block)
    


    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        alternative = result.alternatives[0]
        print("Transcript: {}".format(alternative.transcript))

        words, starts, ends = ([] for i in range(0,3))
        for word_info in alternative.words:
            words.append(word_info.word)
            starts.append(word_info.start_time.total_seconds())
            ends.append(word_info.end_time.total_seconds())

        duration=np.array(ends)-np.array(starts).tolist()
        
        df = pd.DataFrame(list(zip(words, starts, ends, duration)), 
               columns =['token', 'start','end','duration']) 
        
        fname=os.path.join(path2block,trial+'.csv')
        df.to_csv(fname)
        
# =============================================================================
# WRAP UP
# =============================================================================
# load stimuli       
for block_name in ['LocalGlobal2','LocalGlobal4']: 
    wavs, trials=load_stim(block_name)        
    for speech_file, trial in zip(wavs, trials):
        transcribe_file_with_word_time_offsets(speech_file, trial)