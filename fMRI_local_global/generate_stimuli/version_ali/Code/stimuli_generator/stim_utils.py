#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 00:59:55 2020

@author: czacharo

Updated by avalazem
"""
# =============================================================================
# MODULES AND GLOBALS
# =============================================================================
# modules
import os
import pandas as pd
import numpy as np
import random
import warnings
warnings.filterwarnings("ignore")

# alliases
join = os.path.join
make = os.makedirs
exists = os.path.exists
see = os.listdir
read = pd.read_csv

conditions = ['GSLS', 'GSLD', 'GDLS', 'GDLD']
# =============================================================================
# LOAD THE LEXICON
# =============================================================================
path2lexicon = join(os.path.realpath('../..'), 'Lexicon')


def load_lexicon():
    fname = join(path2lexicon, [f for f in see(
        path2lexicon) if 'french_lexicon' in f][0])
    lexicon = pd.read_pickle(fname)

    return lexicon


def check_that_requested_numbers_are_even(n_trials):
    def checker(x): return x % 2 == 0
    check = [checker(n) for n in n_trials]
    if not all(check):
        raise ValueError("You have provided an non-even value!!")


def pp_checker(lexicon):
    '''
    Make sure that n1,n2,n3 have different stems.
    Returns three indices which will be used to 
    parse the noun dict.
    '''
    nouns = lexicon['nouns']['sing']
    num_to_select = 3
    list_of_random_items = random.sample(nouns, num_to_select)
    indices = np.intersect1d(
        nouns, list_of_random_items, return_indices=True)[1]

    # n1,n2,n3=indices

    return indices

# =============================================================================
#
#   Probe Word Generation
#
# =============================================================================

def generate_probe_word(components_info, lexicon, det2_articles=None):
    """
    Generates a probe word based on the components of a sentence.

    This function aims for a 50/50 distribution of *intentions* to either return
    the original word from a randomly selected component or attempt to find a
    replacement word. It maintains a shuffled pool of these intentions (e.g.,
    10 "original", 10 "replacement") and draws one for each call. When the pool
    is empty, it's refilled and reshuffled. This ensures a random spread
    and an equal number of intended true/false outcomes over blocks of calls.

    If a replacement is intended but a suitable one cannot be found from the
    lexicon (ensuring it's not already in other parts of the sentence),
    the function defaults to returning the original word. The returned boolean
    indicates if the word is the original from the sentence (True) or an
    actual replacement (False).

    Args:
        components_info (list): A list of dictionaries, where each dictionary
                                represents a word component and contains keys
                                like 'value', 'type', 'number' (optional), etc.
        lexicon (dict): The loaded lexicon containing word lists by type and number.
        det2_articles (dict, optional): Dictionary containing articles for the second
                                        determiner position, needed for specific replacements.
                                        Defaults to None.

    Returns:
        tuple(str, bool): A tuple containing:
            - The selected or generated probe word (str).
            - A boolean indicating if the word is the original from the sentence (True) or a replacement (False).
    """
    if not components_info:
        return "", True # Return empty string and True

    # Initialize or replenish the decision pool if necessary
    if not hasattr(generate_probe_word, '_decision_pool') or not generate_probe_word._decision_pool:
        pool_size_each = 20  # Number of True (original) and False (replacement) intentions
        choices = [True] * pool_size_each + [False] * pool_size_each
        random.shuffle(choices)
        generate_probe_word._decision_pool = choices
    
    # Pop a decision for the current call: True means intend to use original, False means intend to replace
    intend_to_use_original = generate_probe_word._decision_pool.pop()

    # Randomly select one component info dict
    selected_component_info = random.choice(components_info)
    selected_word_value = selected_component_info['value']

    if intend_to_use_original:
        return selected_word_value, True
    else:
        # --- Replacement Logic ---
        replacement_word = None
        is_original_word = True # Assume fallback to original initially

        # Get other words in the sentence (lowercase) to check against replacements
        other_original_words_lower = {
            comp['value'].lower() for comp in components_info
            if comp['value'].lower() != selected_word_value.lower()
        }

        comp_type = selected_component_info['type']
        number = selected_component_info.get('number')
        should_capitalize = selected_component_info.get('capitalize', False)

        candidates = []
        try:
            if comp_type == 'article':
                candidates = list(lexicon['articles'].get(number, []))
            elif comp_type == 'noun':
                candidates = list(lexicon['nouns'].get(number, []))
            elif comp_type == 'preposition_pp':
                candidates = list(lexicon['prepositions'].get('pp', []))
            elif comp_type == 'preposition_obj':
                # Replace 'que' with a 'pp' preposition
                candidates = list(lexicon['prepositions'].get('pp', []))
            elif comp_type == 'article_pos2':
                if det2_articles and number in det2_articles:
                    candidates = list(det2_articles[number])
                else: # Fallback
                    candidates = list(lexicon['articles'].get(number, []))
            elif comp_type == 'v1':
                candidates = list(lexicon['v1'].get(number, []))
            elif comp_type == 'v2':
                 candidates = list(lexicon['v2'].get(number, []))
            elif comp_type == 'v2_goes_with':
                source_list = selected_component_info.get('source_list', [])
                candidates = [c.strip() for c in source_list if c.strip()]

            # Shuffle candidates to try different ones
            random.shuffle(candidates)

            for candidate in candidates:
                candidate_clean = candidate.strip()
                # Check if candidate is different from original and not in other sentence words
                if (candidate_clean.lower() != selected_word_value.lower() and
                        candidate_clean.lower() not in other_original_words_lower):
                    replacement_word = candidate_clean
                    # Apply capitalization if needed (e.g., first word)
                    if should_capitalize:
                         # Capitalize articles, prepositions if they start the sentence
                         # Nouns/verbs usually aren't capitalized mid-sentence unless proper nouns (not handled here)
                         if comp_type in ['article', 'preposition_pp']:
                             replacement_word = replacement_word.capitalize()
                         # Add other capitalization rules if necessary
                    is_original_word = False # Found a valid replacement
                    break # Stop searching once a valid replacement is found

        except Exception as e:
            # Optional: Log the error
            # print(f"Error finding/checking replacement for {selected_word_value} (type {comp_type}): {e}")
            pass # Fallback to original word below

        # Return the result
        if not is_original_word and replacement_word is not None:
             return replacement_word, False # Return successful replacement
        else:
             # Fallback to original if no suitable replacement found or error occurred
             return selected_word_value, True

# =============================================================================
#
#   Lonng Range Nested PP
#
# =============================================================================
def get_lr_pp_stimuli(condition, g_number, lexicon, indices, soa):

    definit_articles = {}
    definit_articles['sing'] = 'du'
    definit_articles['plur'] = 'des'

    collector = {}
    collector['condition'] = condition
    collector['structure'] = 'lr_pp'
    #collector['filler'] = 'no'
    # =========================================================================
    #   GSLS
    # =========================================================================
    if condition == 'GSLS':

        collector['violation'] = 'no'
        collector['congruency'] = 'yes'
        collector['interference'] = 'no'
        collector['viol_loc'] = 'None'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'sing'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'plur'
            det_2_number = 'plur'
            v1_number = 'plur'
            det_3_number = 'plur'
            n3_number = 'plur'

    # =========================================================================
    #   GSLD
    # =========================================================================
    elif condition == 'GSLD':

        collector['violation'] = 'no'
        collector['congruency'] = 'no'
        collector['interference'] = 'yes'
        collector['viol_loc'] = 'None'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'plur'
            n2_number = 'plur'
            v1_number = 'sing'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'plur'
            det_3_number = 'plur'
            n3_number = 'plur'

    # =========================================================================
    #   GDLS
    # =========================================================================
    elif condition == 'GDLS':

        collector['violation'] = 'yes'
        collector['congruency'] = 'no'
        collector['interference'] = 'no'
        collector['viol_loc'] = '6'

        if g_number == 'sing':
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'plur'
            n2_number = 'plur'
            v1_number = 'plur'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'sing'
            det_3_number = 'plur'
            n3_number = 'plur'

    # =========================================================================
    #   GDLD
    # =========================================================================
    elif condition == 'GDLD':

        collector['violation'] = 'yes'
        collector['congruency'] = 'yes'
        collector['interference'] = 'yes'
        collector['viol_loc'] = '6'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'sing'
            n2_number = 'sing'
            v1_number = 'plur'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'plur'
            det_2_number = 'plur'
            v1_number = 'sing'
            det_3_number = 'plur'
            n3_number = 'plur'

    collector['n1_number'] = n1_number
    collector['n2_number'] = n2_number
    collector['v1_number'] = v1_number

    # tokens
    det_1 = random.sample(lexicon['articles'][det_1_number], 1)[0].capitalize()
    n1 = lexicon['nouns'][n1_number][indices[0]]
    preposition = random.sample(lexicon['prepositions']['pp'], 1)[0]
    det_2 = definit_articles[det_2_number]
    n2 = lexicon['nouns'][n2_number][indices[1]]
    v1 = random.sample(lexicon['v1'][v1_number], 1)[0]
    det_3 = random.sample(lexicon['articles'][det_3_number], 1)[0]
    n3 = lexicon['nouns'][n3_number][indices[2]]

    sentence = det_1 + ' ' + n1 + ' ' + preposition + ' ' + det_2\
        + ' ' + n2 + ' ' + v1 + ' ' + det_3 + ' ' + n3 + '.'

    collector['n1'] = n1
    collector['n2'] = n2
    collector['v1'] = v1

    collector['sentence'] = sentence
    collector['modality'] = soa

    # --- Add probe_word logic ---
    components_info = [
        {'value': det_1, 'type': 'article', 'number': det_1_number, 'capitalize': True},
        {'value': n1, 'type': 'noun', 'number': n1_number},
        {'value': preposition, 'type': 'preposition_pp'},
        {'value': det_2, 'type': 'article', 'number': det_2_number}, # definit_articles used here
        {'value': n2, 'type': 'noun', 'number': n2_number},
        {'value': v1, 'type': 'v1', 'number': v1_number},
        {'value': det_3, 'type': 'article', 'number': det_3_number},
        {'value': n3, 'type': 'noun', 'number': n3_number}
    ]
    probe_word, is_probe_original = generate_probe_word(components_info, lexicon)
    collector['probe_word'] = probe_word
    collector['probe'] = is_probe_original
    # --- End probe_word logic ---

    return collector


def make_lr_pp_stimuli(trials_per_gr_number, lexicon, soa):
    trials = []
    for condition in conditions:
        for g_number in ['sing', 'plur']:
            for trial in range(0, trials_per_gr_number):
                indices = pp_checker(lexicon)
                trials.append(get_lr_pp_stimuli(condition,
                                             g_number, lexicon, indices, soa))
    # concatenate pp-trials
    pp_df = pd.DataFrame(trials)

    return pp_df

# =============================================================================
#
#   Short Range Beginning PP
#
# =============================================================================
def get_sr_pp_stimuli(condition, g_number, lexicon, indices, soa):

    definit_articles = {}
    definit_articles['sing'] = 'du'
    definit_articles['plur'] = 'des'

    collector = {}
    collector['condition'] = condition
    collector['structure'] = 'sr_pp'
    #collector['filler'] = 'no'
    # =========================================================================
    #   GS
    # =========================================================================
    if condition == 'GS':

        collector['violation'] = 'no'
        collector['congruency'] = 'yes'
        collector['interference'] = 'no'
        collector['viol_loc'] = 'None'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'sing'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'plur'
            det_2_number = 'plur'
            v1_number = 'plur'
            det_3_number = 'plur'
            n3_number = 'plur'

    # =========================================================================
    #   GD
    # =========================================================================
    elif condition == 'GD':

        collector['violation'] = 'yes'
        collector['congruency'] = 'yes'
        collector['interference'] = 'yes'
        collector['viol_loc'] = '6'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'sing'
            n2_number = 'sing'
            v1_number = 'plur'
            det_3_number = 'sing'
            n3_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'plur'
            det_2_number = 'plur'
            v1_number = 'sing'
            det_3_number = 'plur'
            n3_number = 'plur'

    collector['n1_number'] = n1_number
    collector['n2_number'] = n2_number
    collector['v1_number'] = v1_number

    # tokens
    det_1 = definit_articles[det_1_number]
    n1 = lexicon['nouns'][n1_number][indices[0]]
    preposition = random.sample(lexicon['prepositions']['pp'], 1)[0].capitalize()
    det_2 = random.sample(lexicon['articles'][det_2_number], 1)[0]
    n2 = lexicon['nouns'][n2_number][indices[1]]
    v1 = random.sample(lexicon['v1'][v1_number], 1)[0]
    det_3 = random.sample(lexicon['articles'][det_3_number], 1)[0]
    n3 = lexicon['nouns'][n3_number][indices[2]]

    sentence = preposition + ' ' + det_1 + ' ' + n1 + ' ' + det_2\
    + ' ' + n2 + ' ' + v1 + ' ' + det_3 + ' ' + n3 + '.'

    collector['n1'] = n1
    collector['n2'] = n2
    collector['v1'] = v1

    collector['sentence'] = sentence
    collector['modality'] = soa

    # --- Add probe_word logic ---
    components_info = [
        {'value': preposition, 'type': 'preposition_pp', 'capitalize': True},
        {'value': det_1, 'type': 'article', 'number': det_1_number}, # definit_articles used here
        {'value': n1, 'type': 'noun', 'number': n1_number},
        {'value': det_2, 'type': 'article', 'number': det_2_number},
        {'value': n2, 'type': 'noun', 'number': n2_number},
        {'value': v1, 'type': 'v1', 'number': v1_number},
        {'value': det_3, 'type': 'article', 'number': det_3_number},
        {'value': n3, 'type': 'noun', 'number': n3_number}
    ]
    probe_word, is_probe_original = generate_probe_word(components_info, lexicon)
    collector['probe_word'] = probe_word
    collector['probe'] = is_probe_original
    # --- End probe_word logic ---

    return collector


def make_sr_pp_stimuli(trials_per_gr_number, lexicon, soa):
    trials = []
    for condition in ['GS', 'GD']: # only GS and GD
        for g_number in ['sing', 'plur']:
            for trial in range(0, trials_per_gr_number):
                indices = pp_checker(lexicon)
                trials.append(get_sr_pp_stimuli(condition,
                                             g_number, lexicon, indices, soa))
    # concatenate pp-trials
    pp_df = pd.DataFrame(trials)

    return pp_df

# =============================================================================
#
#   OBJRC CLAUSE
#
# =============================================================================
def get_objrc_stimuli(condition, g_number, lexicon, indices, soa):

    definit_articles = {}
    definit_articles['sing'] = 'du'
    definit_articles['plur'] = 'des'

    det2_articles = {}
    det2_articles['sing'] = ['le', 'ce']
    det2_articles['plur'] = ['les', 'ces']

    collector = {}
    collector['condition'] = condition
    collector['structure'] = 'lr_obj'
    #collector['filler']    = 'no'
    # =========================================================================
    #   GSLS
    # =========================================================================
    if condition == 'GSLS':

        collector['violation'] = 'no'
        collector['congruency'] = 'yes'
        collector['interference'] = 'no'
        collector['viol_loc'] = 'None'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'sing'
            v2_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'plur'
            det_2_number = 'plur'
            v1_number = 'plur'
            v2_number = 'plur'

    # =========================================================================
    #   GSLD
    # =========================================================================
    elif condition == 'GSLD':

        collector['violation'] = 'yes'
        collector['congruency'] = 'no'
        collector['interference'] = 'no'
        collector['viol_loc'] = '6'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'plur'
            n2_number = 'plur'
            v1_number = 'sing'
            v2_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            n2_number = 'sing'
            det_2_number = 'sing'
            v1_number = 'plur'
            v2_number = 'plur'

    # =========================================================================
    #   GDLS
    # =========================================================================
    elif condition == 'GDLS':

        collector['violation'] = 'no'
        collector['congruency'] = 'no'
        collector['interference'] = 'yes'
        collector['viol_loc'] = 'None'

        if g_number == 'sing':
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'plur'
            n2_number = 'plur'
            v1_number = 'plur'
            v2_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            det_2_number = 'sing'
            n2_number = 'sing'
            v1_number = 'sing'
            v2_number = 'plur'

    # =========================================================================
    #   GDLD
    # =========================================================================
    elif condition == 'GDLD':

        collector['violation'] = 'yes'
        collector['congruency'] = 'yes'
        collector['interference'] = 'yes'
        collector['viol_loc'] = '6'

        if g_number == 'sing':
            # numbers
            det_1_number = 'sing'
            n1_number = 'sing'
            det_2_number = 'sing'
            n2_number = 'sing'
            v1_number = 'plur'
            v2_number = 'sing'

        elif g_number == 'plur':
            # numbers
            det_1_number = 'plur'
            n1_number = 'plur'
            det_2_number = 'plur'
            n2_number = 'plur'
            v1_number = 'sing'
            v2_number = 'plur'

    collector['n1_number'] = n1_number
    collector['n2_number'] = n2_number
    collector['v1_number'] = v1_number

    # remove the indefinite article from the second position due to the
    # presence of the word "que"
    pos_2_articles = {}
    pos_2_articles['sing'] = ['le', 'ce']
    pos_2_articles['plur'] = ['les', 'ces']

    # tokens
    det_1 = random.sample(lexicon['articles'][det_1_number], 1)[0].capitalize()
    n1 = lexicon['nouns'][n1_number][indices[0]]
    preposition = lexicon['prepositions']['obj']
    det_2 = random.sample(det2_articles[det_2_number], 1)[0]
    n2 = lexicon['nouns'][n2_number][indices[1]]
    v1 = random.sample(lexicon['v1'][v1_number], 1)[0]
    v2 = random.sample(lexicon['v2'][v2_number], 1)[0]
    _, where_is_v2, _ = np.intersect1d(
        lexicon['v2'][v2_number], v2, return_indices=True)

    last_words_list = []
    if where_is_v2.size > 0 and where_is_v2[0] < len(lexicon['v2_goes_with']):
        last_words_str = lexicon['v2_goes_with'][where_is_v2[0]].strip()
        last_words_list = [word.strip() for word in last_words_str.split(",") if word.strip()]
    else:
        # Fallback if index is out of bounds or not found
        last_words_list = ['default_word'] # Provide a default or handle error
        print(f"Warning: Could not find matching v2_goes_with for v2: {v2}")

    last_word = random.choice(last_words_list) if last_words_list else 'default_word' # Handle empty list case


    sentence = det_1 + ' ' + n1 + ' ' + preposition + ' ' + det_2\
        + ' ' + n2 + ' ' + v1 + ' ' + v2 + ' ' + last_word + '.'

    collector['n1'] = n1
    collector['n2'] = n2
    collector['v1'] = v1

    collector['sentence'] = sentence
    collector['modality'] = soa

    # --- Add probe_word logic ---
    components_info = [
        {'value': det_1, 'type': 'article', 'number': det_1_number, 'capitalize': True},
        {'value': n1, 'type': 'noun', 'number': n1_number},
        {'value': preposition, 'type': 'preposition_obj'}, # 'que'
        {'value': det_2, 'type': 'article_pos2', 'number': det_2_number},
        {'value': n2, 'type': 'noun', 'number': n2_number},
        {'value': v1, 'type': 'v1', 'number': v1_number},
        {'value': v2, 'type': 'v2', 'number': v2_number},
        {'value': last_word, 'type': 'v2_goes_with', 'source_list': last_words_list}
    ]
    probe_word, is_probe_original = generate_probe_word(components_info, lexicon, det2_articles)
    collector['probe_word'] = probe_word
    collector['probe'] = is_probe_original
    # --- End probe_word logic ---

    return collector


def make_obj_stimuli(trials_per_gr_number, lexicon, soa):
    trials = []
    for condition in conditions:
        for g_number in ['sing', 'plur']:
            for trial in range(0, trials_per_gr_number):
                indices = pp_checker(lexicon)
                trials.append(get_objrc_stimuli(condition,
                                                g_number, lexicon, indices, soa))

    # concatenate obj-trials
    obj_df = pd.DataFrame(trials)

    return obj_df

# =============================================================================
#
# FILLERS
#
# =============================================================================


def get_pp_fillers(g_number, lexicon, indices, soa):

    definit_articles = {}
    definit_articles['sing'] = 'du'
    definit_articles['plur'] = 'des'

    collector = {}
    collector['condition'] = 'pp_filler'
    collector['structure'] = 'pp'
    #collector['filler'] = 'yes'
    collector['viol_loc'] = '5'
    collector['violation'] = 'yes'
    collector['congruency'] = 'None'
    collector['interference'] = 'None'

    if g_number == 'sing':
        # numbers
        det_1_number = 'sing'
        n1_number = 'sing'
        n2_number = 'plur'
        det_2_number = 'sing'
        v1_number = 'sing'
        det_3_number = 'sing'
        n3_number = 'sing'

    elif g_number == 'plur':
        # numbers
        det_1_number = 'plur'
        n1_number = 'plur'
        n2_number = 'sing'
        det_2_number = 'plur'
        v1_number = 'plur'
        det_3_number = 'plur'
        n3_number = 'plur'

    collector['n1_number'] = n1_number
    collector['n2_number'] = n2_number
    collector['v1_number'] = v1_number

    # tokens
    det_1 = random.sample(lexicon['articles'][det_1_number], 1)[0].capitalize()
    n1 = lexicon['nouns'][n1_number][indices[0]]
    preposition = random.sample(lexicon['prepositions']['pp'], 1)[0]
    det_2 = definit_articles[det_2_number]
    n2 = random.sample(lexicon['v2'][v1_number], 1)[0]
    v1 = random.sample(lexicon['v1'][v1_number], 1)[0]
    det_3 = random.sample(lexicon['articles'][det_3_number], 1)[0]
    n3 = lexicon['nouns'][n3_number][indices[2]]

    sentence = det_1 + ' ' + n1 + ' ' + preposition + ' ' + det_2\
        + ' ' + n2 + ' ' + v1 + ' ' + det_3 + ' ' + n3 + '.'

    collector['n1'] = n1
    collector['n2'] = n2 # Note: n2 is actually a v2 verb in this filler
    collector['v1'] = v1

    collector['sentence'] = sentence
    collector['modality'] = soa

    # --- Add probe_word logic ---
    components_info = [
        {'value': det_1, 'type': 'article', 'number': det_1_number, 'capitalize': True},
        {'value': n1, 'type': 'noun', 'number': n1_number},
        {'value': preposition, 'type': 'preposition_pp'},
        {'value': det_2, 'type': 'article', 'number': det_2_number}, # definit_articles used here
        {'value': n2, 'type': 'v2', 'number': v1_number}, # n2 is a v2 verb here
        {'value': v1, 'type': 'v1', 'number': v1_number},
        {'value': det_3, 'type': 'article', 'number': det_3_number},
        {'value': n3, 'type': 'noun', 'number': n3_number}
    ]
    probe_word, is_probe_original = generate_probe_word(components_info, lexicon)
    collector['probe_word'] = probe_word
    collector['probe'] = is_probe_original
    # --- End probe_word logic ---

    return collector


def make_pp_fillers(filler_trials, lexicon, soa):
    trials_per_gr_number = int(filler_trials/2)
    trials = []
    for g_number in ['sing', 'plur']:
        for trial in range(0, trials_per_gr_number):
            indices = pp_checker(lexicon)
            trials.append(get_pp_fillers(g_number,
                                         lexicon, indices, soa))
    if filler_trials%2==1:
         indices = pp_checker(lexicon)
         g_number=random.sample(['sing','plur'],1)[0]
         trials.append(get_pp_fillers(g_number,
                                         lexicon, indices, soa))
            
    # concatenate pp-filler trials
    pp_fillers_df = pd.DataFrame(trials)

    return pp_fillers_df


def get_obj_fillers(g_number, lexicon, indices, soa):

    definit_articles = {}
    definit_articles['sing'] = 'du'
    definit_articles['plur'] = 'des'


    det2_articles = {}
    det2_articles['sing'] = ['le', 'ce']
    det2_articles['plur'] = ['les', 'ces']


    collector = {}
    collector['condition'] = 'obj_filler'
    collector['structure'] = 'obj'
    #collector['filler'] = 'yes'
    collector['viol_loc'] = '7'
    collector['violation'] = 'yes'
    collector['congruency'] = 'None'
    collector['interference'] = 'None'

    if g_number == 'sing':
        # numbers
        det_1_number = 'sing'
        n1_number = 'sing'
        n2_number = 'sing'
        det_2_number = 'sing'
        v1_number = 'sing'
        v2_number = 'plur'

    elif g_number == 'plur':
        # numbers
        det_1_number = 'plur'
        n1_number = 'plur'
        n2_number = 'plur'
        det_2_number = 'plur'
        v1_number = 'plur'
        v2_number = 'sing'

    collector['n1_number'] = n1_number
    collector['n2_number'] = n2_number
    collector['v1_number'] = v1_number

    # tokens
    det_1 = random.sample(lexicon['articles'][det_1_number], 1)[0].capitalize()
    n1 = lexicon['nouns'][n1_number][indices[0]]
    preposition = lexicon['prepositions']['obj']
    det_2 = random.sample(det2_articles[det_2_number], 1)[0]
    n2 = lexicon['nouns'][n2_number][indices[1]]
    v1 = random.sample(lexicon['v1'][v1_number], 1)[0]
    # Original v2 selection (determines last_word)
    original_v2_list = lexicon['v2'][v2_number]
    original_v2 = random.sample(original_v2_list, 1)[0]
    _, where_is_v2, _ = np.intersect1d(
        original_v2_list, original_v2, return_indices=True) # Find index in the correct number list
    # Get last words based on original_v2's index
    # Ensure v2_goes_with has corresponding entry
    last_words_list = []
    if where_is_v2.size > 0 and where_is_v2[0] < len(lexicon['v2_goes_with']):
        last_words_str = lexicon['v2_goes_with'][where_is_v2[0]].strip()
        last_words_list = [word.strip() for word in last_words_str.split(",") if word.strip()]
    else:
        # Fallback if index is out of bounds or not found
        last_words_list = ['default_word'] # Provide a default or handle error
        print(f"Warning: Could not find matching v2_goes_with for v2: {original_v2}")


    last_word = random.choice(last_words_list) if last_words_list else 'default_word' # Handle empty list case


    # Overwrite v2 with a noun for the filler sentence!
    v2_final = random.sample(lexicon['nouns'][n1_number], 1)[0] # Using n1_number based on code


    sentence = det_1 + ' ' + n1 + ' ' + preposition + ' ' + det_2\
        + ' ' + n2 + ' ' + v1 + ' ' + v2_final + ' ' + last_word + '.'

    collector['n1'] = n1
    collector['n2'] = n2
    collector['v1'] = v1

    collector['sentence'] = sentence
    collector['modality'] = soa

    # --- Add probe_word logic ---
    components_info = [
        {'value': det_1, 'type': 'article', 'number': det_1_number, 'capitalize': True},
        {'value': n1, 'type': 'noun', 'number': n1_number},
        {'value': preposition, 'type': 'preposition_obj'}, # 'que'
        {'value': det_2, 'type': 'article_pos2', 'number': det_2_number},
        {'value': n2, 'type': 'noun', 'number': n2_number},
        {'value': v1, 'type': 'v1', 'number': v1_number},
        {'value': v2_final, 'type': 'noun', 'number': n1_number}, # It's a noun in the filler
        {'value': last_word, 'type': 'v2_goes_with', 'source_list': last_words_list} # Associated word
    ]
    probe_word, is_probe_original = generate_probe_word(components_info, lexicon, det2_articles)
    collector['probe_word'] = probe_word
    collector['probe'] = is_probe_original
    # --- End probe_word logic ---

    return collector


def make_obj_fillers(filler_trials, lexicon, soa):
    trials_per_gr_number = int(filler_trials/2)
    trials = []
    for g_number in ['sing', 'plur']:
        for trial in range(0, trials_per_gr_number):
            indices = pp_checker(lexicon)
            trials.append(get_obj_fillers(g_number,
                                          lexicon, indices, soa))
            
    if filler_trials%2==1:
        indices = pp_checker(lexicon)
        g_number=random.sample(['sing','plur'],1)[0]
        trials.append(get_obj_fillers(g_number,
                                        lexicon, indices, soa))
    # concatenate obj-filler trials
    obj_fillers_df = pd.DataFrame(trials)

    return obj_fillers_df
