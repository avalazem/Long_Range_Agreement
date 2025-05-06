import os

import pandas as pd
import numpy as np


MIN_STAR_POS = 5
STAR_ID = 0

def shuffleStimuli(trial):

    ordered_stim = trial.stim
    list_stim = ordered_stim.split(' ')
    np.random.shuffle(list_stim)
  
    # Add star if needed
    if trial.hasStar:
        n_stim  = len(list_stim)
        starPosition = np.random.randint(MIN_STAR_POS, n_stim)
        list_stim[starPosition] = f'{STAR_ID:02}'

    stim = ' '.join(list_stim)

    return stim


def generateSubjectCsv(fname, ordered_csv_file):

    df = pd.read_csv(ordered_csv_file)

    # Shuffle Trials
    subj_df = df[['cond', 'hasStar']].transform(np.random.permutation)

    # Shuffle Rests (keeping last rest as it is)
    ordered_rests = np.array(df['rest'])
    late_blank_duration = ordered_rests[-1]
    rests = np.append(np.random.permutation(ordered_rests[:-1]),
                      late_blank_duration)
    subj_df['rest'] = rests


    # Shuffle stimuli in each trial
    subj_df['stim'] = df['stim']
    stim = subj_df.apply(shuffleStimuli, axis=1)
    subj_df['stim'] = stim

    # Save stim file
    subj_df.to_csv(fname, index=False)

    return subj_df


for SUBJ_ID in range(2):
    fname = f"StimuliOrder/sub-{SUBJ_ID:03}_stimuli.csv"
    o_fname = "ordered_stimuli.csv"
    generateSubjectCsv(fname, o_fname)
