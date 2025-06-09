#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 18:21:40 2020

@author: czacharo
"""

# =============================================================================
# MODULES AND GLOBALS
# =============================================================================
#modules
import os 
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# alliases
join=os.path.join
make=os.makedirs
exists=os.path.exists
see=os.listdir
read=pd.read_csv


# Path to sources
path2sources=join(os.path.realpath('../..'),'Sources')

# =============================================================================
# FETCH DATA FROM SOURCES
# =============================================================================
def fetch_data():

    professions=read(join(path2sources, 
                                 [f for f in see(path2sources) if 'nouns' in f][0]),
                            header=None, names=['nouns',])
    
    lexique=read(join(path2sources, 
                                 [f for f in see(path2sources) if 'noun_lexique' in f][0]))

    data={}
    data['sing'] =professions
    data['lexique']=lexique.astype(str)
    
    return data


# =============================================================================
# ADD FREQUENCY & Number of Letters
# =============================================================================
def add_freq_and_nl(data):
    
    def f(x):
        try:
            l=len(x)
        except TypeError:
            l=0
        return l
    
    # SING
    common_nouns,_,_=np.intersect1d(data['sing'], data['lexique'].Word, 
                                    return_indices=True)
    _,indices,_=np.intersect1d(data['sing'],common_nouns, return_indices=True)
    data['sing']=data['sing'].iloc[indices]
    
    _,_,comm2=np.intersect1d(data['sing'], data['lexique'].Word, 
                                    return_indices=True)
    prof_frequencies=data['lexique'].loc[comm2].freqfilms2#.apply(lambda x:\
                                                                # x.replace(',','.')).astype(float)
    professions=pd.DataFrame(columns=['sing','sing_freq'])
    professions.sing=common_nouns
    professions.sing_freq=prof_frequencies.values.tolist()
    professions.sing_freq=professions.sing_freq.astype('float')    
    professions['plur']=professions.sing.apply(lambda x: x+'s')
    professions=professions.mask(professions.eq('None')).dropna()
    professions.sort_values('sing_freq', ascending=False, inplace=True)

    

    return professions

def remove_vowels(professions):
    vowels = ["a","e","i","o","u", "é"]
    professions=professions[~professions.sing.apply(lambda x: x[0].lower() in vowels)]
    professions=professions[~professions.sing.apply(lambda x: x[0].lower()=='h' )]
    
    return professions

def add_nl(professions):
    professions_sing_nl=professions.sing.apply(lambda x: len(x))
    professions_plur_nl=professions_sing_nl+1
    
    professions['sing_nl']=professions_sing_nl
    professions['plur_nl']=professions_plur_nl
    
    return professions


def select_nouns_based_on_len(professions, lower_bound=3, upper_bound=9):

    professions=professions[professions.plur_nl<=upper_bound]
    professions=professions[professions.plur_nl>=lower_bound]
    professions=professions.reset_index(drop=True)
    
    return professions

def store(professions):
    path2out=join(os.path.realpath('../..'),'Output')
    if not exists(path2out): make(path2out)
    
    professions_fname=join(path2out, 'professions.csv')
    professions.to_csv(professions_fname, encoding='utf-8', index=False)




# =============================================================================
# COMPILE
# =============================================================================
data=fetch_data()
professions=add_freq_and_nl(data)
professions=add_nl(professions)
professions=remove_vowels(professions)
professions=select_nouns_based_on_len(professions, lower_bound=3, upper_bound=9)
store(professions)