#! /usr/bin/env python


""" This program reads a list of stimuli (text, images, sounds) and the
associated onset times from a bunch of csv files.
It then presents them at the requested times. """

import os.path as op
import optparse
import pandas as pd

import expyriment.control
from expyriment import stimuli

from generateSubjectCsv import *


parser = optparse.OptionParser()

parser.add_option('-s', '--idSubject',
                  dest='subjectId',
                  type='int',
                  help='Subject id (order of arrival)')

parser.add_option('-g', '--genCsv',
                  action='store_true',
                  dest='generate_participant_csv',
                  default=False,
                  help='Produce the participant csv')

parser.add_option('-w', '--windowedDisplay',
                  action='store_false',
                  dest='full_screen',
                  default=True,
                  help='Toggle windowed siplay')

(options, args) = parser.parse_args()

SUBJ_ID = options.subjectId
GENERATE_PARTICIPANT_CSV = options.generate_participant_csv
FULL_SCREEN = options.full_screen

###############################################################################
# Defining constants
###############################################################################
WINDOW_SIZE = (1220, 768)
BACKGROUND_COLOR = (0, 0, 0)

TEXT_SIZE = 48
TEXT_COLOR = ( 128, 128, 128)

N_T_WAIT = 1 # number of TTL to wait for at the start

EARLY_BLANK_DURATION = 6000
LATE_BLANK_DURATION = 6000

MAX_BLOCK_DURATION = 438000  # time in milliseconds


# Clicks
MRI_SYNC_KEY = expyriment.misc.constants.K_t

KEY_TRANSLATION = {
    expyriment.misc.constants.K_y: 'y' # Changed to only allow 'y' (left hand button presses in fMRI scanner)
}
AUTHORIZED_KEYS = KEY_TRANSLATION.keys()
KEYPRESS_DELAY = 100

# Experimental Design
CONDITIONS = [ 'face',
               'emoji',
               'wordEF',
               'wordC',
               'Mu'
               ]

# Picture flashed
PICTURE_DURATION = 100
PICTURE_ISI = 300
REST_DURATIONS = [6000]

# Fixation Dot
DOT_SIZE = 4
DOT_COLOR = (26, 167, 19)

# Stimuli directory
STIM_DIR = r"visual_categories"

# Other
STAR_ID = 0

##############################################################################
# Defining files to load : instruction and stimuli list in a csv file
##############################################################################

condition_file = f"sub1_vis.csv"

if (GENERATE_PARTICIPANT_CSV or (not (os.path.isfile(condition_file)))) :
    orderded_stimuli_file = 'ordered_stimuli.csv'
    generateSubjectCsv(condition_file, orderded_stimuli_file)

##############################################################################
# Initiating Expyriment and designing non-specific stimuli : cross, blanck...
##############################################################################

if not FULL_SCREEN :
    expyriment.control.defaults.window_mode = True
    expyriment.control.defaults.window_size = WINDOW_SIZE
expyriment.design.defaults.experiment_background_colour = BACKGROUND_COLOR

exp = expyriment.design.Experiment(
    name="Visualcat_Localizer",
    background_colour=BACKGROUND_COLOR)

expyriment.control.initialize(exp)

exp._screen_colour = BACKGROUND_COLOR
kb = expyriment.io.Keyboard()

# Blank screen
bs = stimuli.Picture(os.path.join(STIM_DIR,
                                  "stimblank.png"))
bs.preload

# Fixation dot
fixationDot = stimuli.Circle(radius=DOT_SIZE, colour=DOT_COLOR)
fixationDot.preload()

# Star
star = stimuli.Picture(os.path.join(STIM_DIR,
                                    "Star.png"))
star.preload

# Instructions
instruction_text = """Appuyez le bouton quand vous voyez une étoile."""
wm = stimuli.TextLine(instruction_text,
                      text_size=TEXT_SIZE,
                      text_colour=TEXT_COLOR,
                      background_colour=BACKGROUND_COLOR)
wm.preload

# Endscreen
endStimulus = stimuli.TextLine( 'Merci !', 
                                text_size = TEXT_SIZE,
                                text_colour = TEXT_COLOR,
                                background_colour = BACKGROUND_COLOR )
endStimulus.preload 


##############################################################################
# Designing block and loading stimuli
##############################################################################

conditions = pd.read_csv(condition_file)

bp = op.dirname(condition_file)

exp.add_data_variable_names(["trial_id",
                             "target_time",
                             "start_time",
                             "end_time",
                             "is_late",
                             "cond",
                             "hasStar",
                             "stim"])

# Block
mappict = dict()
mappict["Star.png"] = star

block = expyriment.design.Block(name="VisualCategory")

NextOnset = EARLY_BLANK_DURATION

for i, row in conditions.iterrows():

    trial = expyriment.design.Trial()

    stimOrder = row.stim.split(' ')
    onset = int(NextOnset)
    cond = row.cond
    rest = row.rest
    trial.set_factor('trial_id', i)
    trial.set_factor('cond', cond)
    trial.set_factor('onset', onset)
    trial.set_factor('hasStar', row.hasStar)
    trial.set_factor('stimuli', row.stim)
    trial.set_factor('rest', rest)

    stim_duration = 0
    for id in stimOrder:
        picture = f"{cond}{id}.png"

        if int(id) == STAR_ID :
            picture = "Star.png"

        if picture not in mappict:
            mappict[picture] = stimuli.Picture(os.path.join(
                STIM_DIR,
                picture))
            mappict[picture].preload()

            
        trial.add_stimulus(mappict[picture])
        stim_duration += PICTURE_ISI

    NextOnset = onset + stim_duration + rest

    block.add_trial(trial)

exp.add_block(block)


###############################################################################
# Functions for stim presentation
###############################################################################

def present(stim):

    stim.present(clear=True, update=False)
    fixationDot.present(clear=False, update=True)


def wait_for_mri_sync(n_t_wait):

    t_signal_count = 0
    while t_signal_count < n_t_wait :
        kb.wait(MRI_SYNC_KEY)
        present(bs)
        t_signal_count += 1


def check_key_until(target_time):

    while exp.clock.stopwatch_time < target_time:
        
        code = exp.keyboard.check(keys=AUTHORIZED_KEYS)
        
        if code != None:
            key = KEY_TRANSLATION[code]
            time = exp.clock.stopwatch_time
            exp.data.add([
                'button pressed',
                key,
                target_time,
                time,
                time + KEYPRESS_DELAY,
                f"rt: {(time + KEYPRESS_DELAY) - target_time}",])
        
        # exp.clock.wait(1)


def check_key_for(duration):

    time = exp.clock.stopwatch_time
    target_time = time + duration

    events = check_key_until(target_time)

    return events


###############################################################################
# Starting the protocol
###############################################################################

# Starting experiment
expyriment.control.start(
    skip_ready_screen=True,
    subject_id=SUBJ_ID)


for block in exp.blocks:
    
    wm.present()
    wait_for_mri_sync(N_T_WAIT)
    
    # Reset keyboard, screen, stopwatch
    kb.clear()
    present(bs)
    exp.clock.reset_stopwatch()

    # Presenting stimuli
    for trial in block.trials:

        # Get factors
        trial_id = trial.get_factor('trial_id')
        cond = trial.get_factor('cond')
        target_time = trial.get_factor('onset')
        hasStar = trial.get_factor('hasStar')
        stimuli = trial.get_factor('stimuli')
        rest = trial.get_factor('rest')
        events = []

        # Wait until begining of trial
        is_late = exp.clock.stopwatch_time > target_time
        check_key_until(target_time)
        
        # Present stimulus
        start_time = exp.clock.stopwatch_time
        for stim in trial.stimuli:

            stim_start_time = exp.clock.stopwatch_time

            present(stim)
            
            check_key_for(PICTURE_DURATION)
            
            present(bs)

            presentation_duration = exp.clock.stopwatch_time - stim_start_time
            check_key_for(PICTURE_ISI - presentation_duration)
            
        end_time = exp.clock.stopwatch_time


        # Save data
        exp.data.add( [ trial_id,
                        target_time,
                        start_time,
                        end_time,
                        is_late,
                        cond,
                        hasStar,
                        stimuli ] )

    check_key_for(LATE_BLANK_DURATION)

    end_block = exp.clock.stopwatch_time

    exp.data.add(['endstim',
                  MAX_BLOCK_DURATION,
                  end_block,
                  end_block,
                  MAX_BLOCK_DURATION < end_block,
                  'endstim',
                  'endstim',
                  'endstim'])

expyriment.control.end('Merci !', 2000)
