#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module:
    1.Loads data with verbs of the second and third group 
    parsed from the Wiktionary.
    2. Conjugates them in the 3rd singular and 3rd plural. 
    3. Adds as a feature their frequency (for the infinitive form) from 
    lexique.org
    4. Translates them to English. 
    5. Adds as a feature the number of letters and their difference. 
    6. Adds as a feature the Levenshtein metric. 
"""
# =============================================================================
# MODULES AND GLOBALS
# =============================================================================
#modules
import os 
import pandas as pd
import numpy as np
import mlconjug
from Levenshtein import distance
from textblob import TextBlob
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

# To use mlconjug with the default parameters and a pre-trained conjugation model.
default_conjugator = mlconjug.Conjugator(language='fr')
conjugate=default_conjugator.conjugate
conj_3s=lambda x: conjugate(x).conjug_info['Indicatif']['Présent']['3s']
conj_3p=lambda x: conjugate(x).conjug_info['Indicatif']['Présent']['3p']
# =============================================================================
# FETCH DATA FROM SOURCES
# =============================================================================
def fetch_data():

    second_group_verbs=read(join(path2sources, 
                                 [f for f in see(path2sources) if '2nd' in f][0]),
                            header=None, names=['infinitive',])
    
    third_group_verbs=read(join(path2sources, 
                                 [f for f in see(path2sources) if '3rd' in f][0]),
                           header=None, names=['infinitive',])
    lexique=read(join(path2sources, 
                                 [f for f in see(path2sources) if 'verb_lexique' in f][0]))

    data={}
    data['second'] =second_group_verbs
    data['third']  =third_group_verbs
    data['lexique']=lexique
    
    return data

# =============================================================================
# TEXT PREPROCESSING
# =============================================================================
def text_preprocessing(data, lower_bound=3, upper_bound=15):
    ## 1:Remove verbs with more that one syllables (i.e: S'abâtardir or Perdre du poids)
    # -------------------------------------------------------------------------------------
    second_group_verbs=data['second'][~data['second'].applymap(lambda x:\
                                                       (('\'' in x) == True) or\
                                                           ((' ' in x) == True) or\
                                                               (('-' in x) == True))].dropna()
    third_group_verbs=data['third'][~data['third'].applymap(lambda x:\
                                                       (('\'' in x) == True) or\
                                                           ((' ' in x) == True) or\
                                                               (('-' in x) == True))].dropna()

    ## 2: Make lowercase and strip whitespace
    # -------------------------------------------------------------------------------------
    second_group_verbs= second_group_verbs.applymap(lambda x: x.lower())    
    second_group_verbs= second_group_verbs.applymap(lambda x: x.strip())    
    third_group_verbs= third_group_verbs.applymap(lambda x: x.lower())    
    third_group_verbs= third_group_verbs.applymap(lambda x: x.strip())  
    
    ## 3: Remove words based on length
    # -------------------------------------------------------------------------------------
    second_group_verbs=\
        second_group_verbs[second_group_verbs.applymap(lambda x:len(x)>lower_bound and len(x)<upper_bound)].dropna()
    third_group_verbs=\
        third_group_verbs[third_group_verbs.applymap(lambda x: len(x)>lower_bound and len(x)<upper_bound)].dropna()
        
    catch_words=['plus', 'abonnement', 'amateur', 'attendez', 'taches', 'brûlures',
                 'citation', 'décapage', 'dispersion', 'endolori', 'liant', 'sa', 
                 'relax', 'superfin', 'lien', 'crossdress']
    # Now remove catch-words indicated by failed conjugation attempts
    second_group_verbs=\
        second_group_verbs[second_group_verbs.applymap(lambda x: x not in catch_words)].dropna()
        
    
    data['second'] =second_group_verbs
    data['third']  =third_group_verbs
    
    return data
# =============================================================================
# CONJUGATE    
# =============================================================================
# Create a new dataframe with added columns for the conjugations in 3s and 3p
# as well as their corresponding features. 

def congugate_verbs(data):

    print('Conjugating')
    # SECOND GROUP CONJUCATIONS
    second_group_3s= data['second'].applymap(conj_3s)
    second_group_3p= data['second'].applymap(conj_3p)
    # THIRD GROUP CONJUCATIONS
    third_group_3s= data['third'].applymap(conj_3s)
    third_group_3p= data['third'].applymap(conj_3p)
    print('Done')
    
    # Construct full dataframe (second group)
    second=pd.concat([data['second'], second_group_3s, second_group_3p], axis=1)
    second.columns=['infinitive', 'third_s', 'third_p']
    second.reset_index(drop=True, inplace=True)
    
    # Construct full dataframe (third group)
    third=pd.concat([data['third'], third_group_3s, third_group_3p], axis=1)
    third.columns=['infinitive', 'third_s', 'third_p']
    third.reset_index(drop=True, inplace=True)


    return second, third


# =============================================================================
# ADD FREQUENCY & Number of Letters
# =============================================================================
def add_freq_and_nl(second, third, data):
    
    def f(x):
        try:
            l=len(x)
        except TypeError:
            l=0
        return l
    
    # SECOND GROUP 
    common_verbs,df_indices,lex_indices=np.intersect1d(second.infinitive, data['lexique'].lemme, 
                                    return_indices=True)
    freq_common_verbs=data['lexique'].freqfilms2[lex_indices].values  
    second=second.iloc[df_indices]
    # Add to existing dataframe
    second['infitive_freq']=freq_common_verbs
    second['third_s_nl']=second.third_s.apply(lambda x:len(x))
    second['third_p_nl']=second.third_p.apply(lambda x:len(x))    
    second.reset_index(drop=True, inplace=True)
    
    # THIRD GROUP 
    common_verbs,df_indices,lex_indices=np.intersect1d(third.infinitive, data['lexique'].lemme, 
                                    return_indices=True)
    freq_common_verbs=data['lexique'].freqfilms2[lex_indices].values      
    third=third.iloc[df_indices]
    # Add to existing dataframe
    third['infitive_freq']=freq_common_verbs
    third['third_s_nl']=third.third_s.apply(f)
    third['third_p_nl']=third.third_p.apply(f)    
    third.reset_index(drop=True, inplace=True)
    
    
    
    return second, third


# =============================================================================
# SORT AND STORE
# =============================================================================
def sort_dfs(second, third):
    second.sort_values('infitive_freq', ascending=False, inplace=True)
    third.sort_values('infitive_freq', ascending=False, inplace=True)
    
    second=second.mask(second.eq('None')).dropna()
    third=third.mask(third.eq('None')).dropna()
    
    return second, third

def remove_first_group_verbs(second, third):
    first_group_suffix=lambda x: x.endswith('er')
    second=second[~second.infinitive.apply(first_group_suffix)]
    third=third[~third.infinitive.apply(first_group_suffix)]

    return second, third

def translate(second, third):
    second_translations, third_translations,\
    second_pos, third_pos=([] for i in range(0,4))
    
    for verb in second.infinitive.values:
        try:
            blob = TextBlob(verb)
            verb_blob=blob.translate(from_lang='fr', to='en')
            second_translations.append(verb_blob.string)
        except:
            second_translations.append('Could not translate')


    for verb in third.infinitive.values:
        try:
            blob = TextBlob(verb)
            verb_blob=blob.translate(from_lang='fr', to='en')
            third_translations.append(verb_blob.string)
        except:
            third_translations.append('Could not translate')



def add_difference_of_conjugation(second, third):
    
    second['l_difference']=second.third_p_nl-second.third_s_nl
    third['l_difference'] =third.third_p_nl-third.third_s_nl
       
    return second, third


def remove_empty_values(second, third):
    third.dropna(inplace=True)
    second.dropna(inplace=True)    
    
    return second, third
def add_levenshtein_difference(second, third):

    lev_distance_second=[distance(second.third_s.values[i],
                           second.third_p.values[i]) for i in range(0,len(second))]
     
    lev_distance_third=[distance(third.third_s.values[i],
                           third.third_p.values[i]) for i in range(0,len(third))]

    second['levenshtein']= lev_distance_second   
    third['levenshtein'] = lev_distance_third
    
    return second, third
        

def store(second, third):
    path2out=join(os.path.realpath('../..'),'Output')
    if not exists(path2out): make(path2out)
    
    second=second.reset_index(drop=True)
    second_fname=join(path2out, 'second_group.csv')
    second.to_csv(second_fname,  encoding='utf-8', index=False)

    third=third.reset_index(drop=True)
    third_fname=join(path2out, 'third_group.csv')
    third.to_csv(third_fname,  encoding='utf-8', index=False)    




def select_verbs_based_on_len(second, third, lower_bound=3, upper_bound=9):

    third=third[(third.third_p_nl<=upper_bound) & (third.third_s_nl<=upper_bound)]
    third=third[(third.third_p_nl>=lower_bound) & (third.third_s_nl>=lower_bound)]
    
    second=second[(second.third_p_nl<=upper_bound) & (second.third_s_nl<=upper_bound)]
    second=second[(second.third_p_nl>=lower_bound) & (second.third_s_nl>=lower_bound)]    
    
    return second, third


#%%
# =============================================================================
# COMPILE
# =============================================================================
data=fetch_data()
data=text_preprocessing(data, lower_bound=2, upper_bound=15)
second, third=congugate_verbs(data)
second, third=remove_empty_values(second, third)
second, third=add_levenshtein_difference(second, third)
# second, third=remove_first_group_verbs(second, third)
second, third=add_freq_and_nl(second, third, data)
second, third=sort_dfs(second, third)
second, third=add_difference_of_conjugation(second, third)
second, third=select_verbs_based_on_len(second, third, lower_bound=3, upper_bound=9)
store(second, third)


    