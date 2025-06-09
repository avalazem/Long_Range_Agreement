#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
We manipulate two structures and two features. The structures are an objRC
and a prepositional phrase. The features are the target of the violation 
(inner or outer). So we have a cell of 4 categories:
    #1: obj_inner
    #2: obj_outer (fillers)
    #3: pp_inner  (fillers)
    #4: pp_outer

For each of these manipulations, we apply the GXLY violation procedure
for singular and plural nouns. 

"""
import os
import pandas as pd
from random import shuffle
import random
from lexicon import words

# =============================================================================
# Extract POS of interest
# =============================================================================

determiner_kinds=['definite', 'demonstrative']
humans = words['humans']
det = words['det']
adv = words['adv']
tran = words['verbs']['tran']
intr = words['verbs']['intr']
activities = words['activities']

verbs_for_pos_violations={}
verbs_for_pos_violations['sing']=['arrives',
                                  'leaves', 'detests',]
verbs_for_pos_violations['plur']=['arrive',
                                  'leave', 'detest', ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DEFINE FEATURES OF INTEREST
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

numbers = ['sing', 'plur']
conditions = ['GSLS', 'GSLD', 'GDLS', 'GDLD']
structures = ['pp', 'obj']
violations = ['inner', 'outer']  # pp-inner=filler, obj-outer=filler
features = ['sentence', 'type', 'structure', 'condition',
            'number', 'violIndex',
            'violation_location', 'filler',
            'violation', 'congruency',	'interference',
            ]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# =============================================================================


def check_n1_n2_stems(n1_index, n2_index, n_entries):
    while True:
        if n2_index == n1_index:
            n2_index = random.choice(range(0, n_entries))
        else:
            break
    return n2_index

def check_last_word_index(last_word_index, n1_index, n2_index):
    while True:
        if last_word_index in (n1_index, n2_index):
            last_word_index = random.choice(range(0, len(humans)))
        else:
            break
    return last_word_index

# =============================================================================
# SENTENCES
# =============================================================================
# return the POS numbers based on the condition and the structure


def pos_numbers(number, opposite_number, condition, structure):
    if structure == 'pp':
        if condition == 'GSLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number, number, number, number)

            violation_index = 0
            filler = 'no'
            violation = 'no'
            congruency = 'yes'
            interference = 'no'

        elif condition == 'GSLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             opposite_number, number, number)

            violation_index = 0
            filler = 'no'
            violation = 'no'
            congruency = 'no'
            interference = 'yes'

        elif condition == 'GDLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             opposite_number, opposite_number, number)

            violation_index = 1
            filler = 'no'
            violation = 'yes'
            congruency = 'no'
            interference = 'no'

        elif condition == 'GDLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number,
                             number, opposite_number, opposite_number)

            violation_index = 1
            filler = 'no'
            violation = 'yes'
            congruency = 'yes'
            interference = 'yes'

    elif structure == 'obj':
        if condition == 'GSLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number, number, number, number)

            violation_index = 0
            filler = 'no'
            violation = 'no'
            congruency = 'yes'
            interference = 'no'

        elif condition == 'GSLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             opposite_number, number, number)

            violation_index = 1
            filler = 'no'
            violation = 'yes'
            congruency = 'no'
            interference = 'no'

        elif condition == 'GDLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             opposite_number, opposite_number, number)

            violation_index = 0
            filler = 'no'
            violation = 'no'
            congruency = 'no'
            interference = 'yes'

        elif condition == 'GDLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number,
                             number, opposite_number, number)

            violation_index = 1
            filler = 'no'
            violation = 'yes'
            congruency = 'yes'
            interference = 'yes'

    return (det_1_number, n1_number,
            det_2_number, n2_number, v1_number, v2_number, violation_index,
            filler, violation, congruency, interference)

# =============================================================================
# FILLERS
# =============================================================================


def filler_pos_numbers(number, opposite_number, condition, structure):
    if structure == 'pp':
        if condition == 'GSLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             number, number, number)

            violation_index = 1

        elif condition == 'GSLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number,
                             opposite_number, number, number)

            violation_index = 1

        elif condition == 'GDLS':
            pass
        elif condition == 'GDLD':
            pass

    elif structure == 'obj':
        if condition == 'GSLS':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, number, number,
                             number, opposite_number)

            violation_index = 1

        # elif condition=='GSLD':
        #     pass

        elif condition == 'GSLD':
            det_1_number,\
                n1_number,\
                det_2_number,\
                n2_number,\
                v1_number,\
                v2_number = (number, number, opposite_number,
                             opposite_number, opposite_number, opposite_number)

            violation_index = 1

        elif condition == 'GDLD':
            pass
    filler = 'yes'
    violation = 'yes'
    congruency = '-'
    interference = '-'
    condition='filler'
    return (det_1_number, n1_number,
            det_2_number, n2_number, v1_number, v2_number, violation_index,
            filler, violation, congruency, interference)


# =============================================================================
# SENTENCES
# =============================================================================
def gram_numbers_per_condition(condition, number, structure):
    '''
    This function currently serves the number condition    

    '''
    curr_number_index = numbers.index(number)
    if curr_number_index == 0:
        opposite_index = 1
        opposite_number = numbers[opposite_index]
    else:
        opposite_index = 0
        opposite_number = numbers[opposite_index]

    det_1_number, n1_number, det_2_number,\
        n2_number, v1_number, v2_number, violation_index,\
        filler, violation, congruency, interference =\
        pos_numbers(number, opposite_number, condition, structure)

    return (det_1_number, n1_number,
            det_2_number, n2_number, v1_number,
            v2_number, violation_index, filler, violation, congruency, interference)

# =============================================================================
# FILLERS
# =============================================================================


def fillers_per_condition(condition, number, structure):
    '''
    This function currently serves the number condition    

    '''
    curr_number_index = numbers.index(number)
    if curr_number_index == 0:
        opposite_index = 1
        opposite_number = numbers[opposite_index]
    else:
        opposite_index = 0
        opposite_number = numbers[opposite_index]

    det_1_number, n1_number, det_2_number,\
        n2_number, v1_number, v2_number, violation_index,\
        filler, violation, congruency, interference =\
        filler_pos_numbers(number, opposite_number, condition, structure)

    return (det_1_number, n1_number,
            det_2_number, n2_number, v1_number,
            v2_number, violation_index, filler, violation, congruency, interference)


# =============================================================================
# SENTENCES
# =============================================================================
def gen_number_sentences(structure, condition, number, container):

    det_1_number, n1_number,\
        det_2_number, n2_number, v1_number,\
        v2_number, violation_index, filler, violation,\
        congruency, interference =\
        gram_numbers_per_condition(condition, number, structure)

    # DET 1
    # ~~~~~~~~~~
    shuffle(determiner_kinds)
    kind=determiner_kinds[0]
        
    determiner_one = det[det_1_number][kind]  # [0]

    # N1
    # ~~~~~~~~~~
    n_entries = len(humans[n2_number])
    n1_index = random.choice(range(0, n_entries))
    n1 = humans[n1_number][n1_index]
    # ADVERB
    # ~~~~~~~~~~
    adverb = adv[structure][0]

    # N2
    # ~~~~~~~~~~

    n2_index = random.choice(range(0, n_entries))
    # Make sure that the stems of N1 and N2 are different
    n2_index = check_n1_n2_stems(n1_index, n2_index, n_entries)
    n2 = humans[n2_number][n2_index]
    # V1
    # ~~~~~~~~~~
    v1_index = random.choice(range(0, len(tran[v1_number])))
    v1 = tran[v1_number][v1_index]

    if structure == 'pp':
        # DET 2
        # ~~~~~~~~~~
        shuffle(determiner_kinds)
        kind=determiner_kinds[0]
        determiner_two = det[det_2_number][kind]  # [0]

        # N3
        # ~~~~~~~~~~
        last_word_index = random.choice(range(0, len(activities)))
        last_word = activities[last_word_index]

        if condition in ('GSLS', 'GSLD'):
            violation_location = 'none'
        else:
            violation_location = 'outer'

    elif structure == 'obj':
        # DET 2
        # ~~~~~~~~~~
        shuffle(determiner_kinds)
        kind=determiner_kinds[0]
        determiner_two = det[det_2_number][kind]  # [0]

        # V2
        # ~~~~~~~~~~
        last_word_index = random.choice(range(0, len(intr[number])))
        last_word = intr[number][last_word_index]

        if condition in ('GSLS', 'GDLS'):
            violation_location = 'none'
        else:
            violation_location = 'inner'

    sentence = (
        determiner_one.capitalize()+' '+n1 + ' '+adverb+' ' +
        determiner_two+' ' +
        n2+' '+v1+' '+last_word+'.')

    container['sentence'].append(sentence)
    container['type'].append('number')
    container['structure'].append(structure)
    container['condition'].append(condition)
    container['number'].append(number)
    container['violIndex'].append(violation_index)
    container['violation_location'].append(violation_location)
    container['filler'].append('no')
    container['violation'].append(violation)
    container['congruency'].append(congruency)
    container['interference'].append(interference)

    return container

# =============================================================================
# FILLERS
# =============================================================================


def gen_fillers(structure, condition,  number, container):

    det_1_number, n1_number,\
        det_2_number, n2_number, v1_number,\
        v2_number, violation_index, filler, violation,\
        congruency, interference =\
        fillers_per_condition(condition, number, structure)

    # DET 1
    # ~~~~~~~~~~
    shuffle(determiner_kinds)
    kind=determiner_kinds[0]
    determiner_one = det[det_1_number][kind]  # [0]

    # N1
    # ~~~~~~~~~~
    n_entries = len(humans[n2_number])
    n1_index = random.choice(range(0, n_entries))
    n1 = humans[n1_number][n1_index]
    # ADVERB
    # ~~~~~~~~~~
    adverb = adv[structure][0]


    # V1
    # ~~~~~~~~~~
    v1_index = random.choice(range(0, len(tran[v1_number])))
    v1 = tran[v1_number][v1_index]

    if structure == 'pp':
        # N2
        # ~~~~~~~~~~
        n2_index = random.choice(range(0, len(verbs_for_pos_violations)))
        # Make sure that the stems of N1 and N2 are different
        # n2_index = check_n1_n2_stems(n1_index, n2_index, n_entries)
        n2 = verbs_for_pos_violations[n1_number][n2_index]


        # DET 2
        # ~~~~~~~~~~
        shuffle(determiner_kinds)
        kind=determiner_kinds[0]
        determiner_two = det[det_1_number][kind]  # [0]

        # N3
        # ~~~~~~~~~~
        last_word_index = random.choice(range(0, len(activities)))
        last_word = activities[last_word_index]

        if condition in ('GDLS', 'GDLD'):
            violation_location = 'none'
        else:
            violation_location = 'inner'

    elif structure == 'obj':
        # N2
        # ~~~~~~~~~~
        n2_index = random.choice(range(0, n_entries))
        # Make sure that the stems of N1 and N2 are different
        n2_index = check_n1_n2_stems(n1_index, n2_index, n_entries)
        n2 = humans[n2_number][n2_index]
        
        
        # DET 2
        # ~~~~~~~~~~
        shuffle(determiner_kinds)
        kind=determiner_kinds[0]
        determiner_two = det[det_2_number][kind]  # [0]

        # V2
        # ~~~~~~~~~~
        last_word_index = random.choice(range(0, len(humans)))

        last_word_index=check_last_word_index(last_word_index, n1_index, n2_index)
        
        
        last_word = humans[v2_number][last_word_index]

        if condition in ('GDLS', 'GDLD'):
            violation_location = 'none'
        else:
            violation_location = 'outer'

    sentence = (
        determiner_one.capitalize()+' '+n1 + ' '+adverb+' ' +
        determiner_two+' ' +
        n2+' '+v1+' '+last_word+'.')

    container['sentence'].append(sentence)
    container['type'].append('number')
    container['structure'].append(structure)
    container['condition'].append('filler')
    container['number'].append(number)
    container['violIndex'].append(violation_index)
    container['violation_location'].append(violation_location)
    container['filler'].append('yes')
    container['violation'].append(violation)
    container['congruency'].append(congruency)
    container['interference'].append(interference)

    return container


# =============================================================================
# FUNCTIONS THAT CREATE THE DATA
# =============================================================================


# =============================================================================
# GENERATE PP STIMULI
# =============================================================================

def generate_pp_stimuli(n_of_pp_trials):
    # initialize dataframe to hold data
    pp_stim = pd.DataFrame(columns=features)

    container = {}
    for f in features:
        container[f] = []

    for trial in range(0,int(n_of_pp_trials/8)): # 8 is the minimal cell
        for number in numbers:
            for condition in conditions:
                container = gen_number_sentences('pp', condition,
                                                 number, container)

    
    pp_stim.sentence = container['sentence']
    pp_stim.type = container['type']
    pp_stim.structure = container['structure']
    pp_stim.condition = container['condition']
    pp_stim.number = container['number']
    pp_stim.violIndex = container['violIndex']
    pp_stim.violation_location = container['violation_location']
    pp_stim.filler = container['filler']
    pp_stim.violation = container['violation']
    pp_stim.congruency = container['congruency']
    pp_stim.interference = container['interference']

    return pp_stim
    
# =============================================================================
# GENERATE OBJRC STIMULI
# =============================================================================
def generate_obj_stimuli(n_of_pp_trials):
    # initialize dataframe to hold data
    obj_stim = pd.DataFrame(columns=features)

    container = {}
    for f in features:
        container[f] = []

    for trial in range(0,int(n_of_pp_trials/8)): # 8 is the minimal cell
        for number in numbers:
            for condition in conditions:
                container = gen_number_sentences('obj', condition,
                                                 number, container)

    
    obj_stim.sentence = container['sentence']
    obj_stim.type = container['type']
    obj_stim.structure = container['structure']
    obj_stim.condition = container['condition']
    obj_stim.number = container['number']
    obj_stim.violIndex = container['violIndex']
    obj_stim.violation_location = container['violation_location']
    obj_stim.filler = container['filler']
    obj_stim.violation = container['violation']
    obj_stim.congruency = container['congruency']
    obj_stim.interference = container['interference']

    return obj_stim
    

def generate_fillers(n_of_pp_fillers, structure):
    # initialize dataframe to hold data
    fillers = pd.DataFrame(columns=features)

    container = {}
    for f in features:
        container[f] = []

    for trial in range(0,int(n_of_pp_fillers)): 
        shuffle(numbers)    
        number=numbers[0]
        shuffle(conditions)
        condition=['GSLS','GSLD'][0]
        container = gen_fillers(structure, condition,
                                        number, container)


    
    fillers.sentence = container['sentence']
    fillers.type = container['type']
    fillers.structure = container['structure']
    fillers.condition = container['condition']
    fillers.number = container['number']
    fillers.violIndex = container['violIndex']
    fillers.violation_location = container['violation_location']
    fillers.filler = container['filler']
    fillers.violation = container['violation']
    fillers.congruency = container['congruency']
    fillers.interference = container['interference']

    return fillers



def store_visual_stimuli(stim_per_block, block_name):
    path2block = os.path.join(
        os.path.realpath('../../run_experiment/Stimuli/visual'),
        block_name)
    if not os.path.exists(path2block):
        os.makedirs(path2block)
    fname = os.path.join(path2block,block_name+'.csv')
    stim_per_block.to_csv(fname)

# %%
# =============================================================================
# WRAP UP AND PRODUCE THE STIMULI
# =============================================================================
join = os.path.join


# set the #blocks, # trials etc
minimal_cell= 8      # 4 conditions X 2 grammatical numbers per structure (e.g: PP)
n_of_reps   = 5      # how many times to repeat the minimal cell 
n_blocks    = 4
block_types = ['visual','auditory', 'visual','auditory',]
visual_block_names= ['LocalGlobal1','' ,'LocalGlobal3','']


# number of trials per block
n_pp_trials  =minimal_cell*n_of_reps
n_obj_trials =minimal_cell*n_of_reps
n_pp_fillers =int(n_pp_trials/minimal_cell)
n_obj_fillers=int(n_obj_trials/minimal_cell)

def define_path(block_type):
    path2stimuli = join(os.path.realpath('../..'),
                    'Stimuli', 'version_07',block_type)
    if not os.path.exists(path2stimuli):
        os.makedirs(path2stimuli)
    return path2stimuli

for block, block_type in zip(range(0, n_blocks), block_types):
    stimuli = []

    stimuli.append(generate_pp_stimuli(n_pp_trials))   # add PP-Trials
    stimuli.append(generate_obj_stimuli(n_obj_trials)) # add Obj-Trials
    stimuli.append(generate_fillers(n_pp_fillers, 'pp')) # add PP-filelrs
    stimuli.append(generate_fillers(n_obj_fillers, 'obj')) # add Obj-filelrs

    stim_per_block = pd.concat(stimuli,
                               ignore_index=True, sort=False)

    # SHUFFLE the dataframe
    stim_per_block = stim_per_block.sample(frac=1)
    # ## OUTPUT as CSV
    
    path2stimuli=define_path(block_type)
    fname = join(path2stimuli, f'block_{block+1}_{block_type}.csv')
    if not os.path.exists(path2stimuli):
        os.makedirs(path2stimuli)
    stim_per_block.to_csv(fname, encoding='utf-8', sep='\t')

    if block_type=='visual':
        # Store in the 'run_experiment' folder
        block_name=visual_block_names[block]
        store_visual_stimuli(stim_per_block, block_name)
