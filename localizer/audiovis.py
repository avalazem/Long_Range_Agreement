#! /usr/bin/env python
# Time-stamp: <2019-03-08 15:57:45 christophe@pallier.org>

""" This program reads a list of stimuli (text, images, sounds) and the associated onset times from a bunch of csv files. It then presents them at the requested times. """

import sys
import io
import os.path as op
import argparse
import pandas as pd

import expyriment.control
from expyriment import stimuli
from expyriment.misc import Clock

from queue import PriorityQueue

# constants (which can be modified by optional command line arguments)
WORD_DURATION = 450
WORD_ISI = 200
PICTURE_DURATION = 3000
PICTURE_ISI = 0
TEXT_DURATION = 200
TOTAL_EXPE_DURATION = -1 # time in millisec
BACKGROUND_COLOR=(0, 0, 0)
TEXT_FONT = 'Inconsolata-Regular.ttf'
TEXT_SIZE = 48
TEXT_COLOR = (240, 240, 240)
#WINDOW_SIZE = (1220, 700)
WINDOW_SIZE = (1280, 1028)

# Ali Added - only allow 'y' key presses
KEY_TRANSLATION = {
    expyriment.misc.constants.K_y: 'y' # Changed to only allow 'y' (left hand button presses in fMRI scanner)
}
AUTHORIZED_KEYS = KEY_TRANSLATION.keys()


# process command line options

parser = argparse.ArgumentParser()
parser.add_argument("--splash", help="displays a picture (e.g. containing instructions) before starting the experiment")

parser.add_argument('csv_files',
                    nargs='+',
                    action="append",
                    default=[])
parser.add_argument('--total-duration',
                    type=int,
                    default=-1,
                    help="time to wait for after the end of the stimuli stream")
parser.add_argument("--rsvp-display-time",
                    type=int,
                    default=WORD_DURATION,
                    help="set the duration of display of single words \
                          in rsvp stimuli")
parser.add_argument("--rsvp-display-isi",
                    type=int,
                    default=WORD_ISI,
                    help="set the duration of display of single words \
                          in rsvp stimuli")
parser.add_argument("--picture-display-time",
                    type=int,
                    default=PICTURE_DURATION,
                    help="set the duration of display of pictures")
parser.add_argument("--picture-isi",
                    type=int,
                    default=PICTURE_ISI,
                    help="set the ISI between pictures in  pictseq sequence")
parser.add_argument("--text-display-time",
                    type=int,
                    default=TEXT_DURATION,
                    help="set the duration of display of text")
parser.add_argument("--text-font",
                    type=str,
                    default=TEXT_FONT,
                    help="set the font for text stimuli")
parser.add_argument("--text-size",
                    type=int,
                    default=TEXT_SIZE,
                    help="set the vertical size of text stimuli")
parser.add_argument("--text-color",
                    nargs='+',
                    type=int,
                    default=TEXT_COLOR,
                    help="set the font for text stimuli")
parser.add_argument("--background-color",
                    nargs='+',
                    type=int,
                    default=BACKGROUND_COLOR,
                    help="set the background color")
parser.add_argument("--window-size",
                    nargs='+',
                    type=int,
                    default=WINDOW_SIZE,
                    help="in window mode, sets the window size")


args = parser.parse_args()
splash_screen = args.splash
WORD_DURATION = args.rsvp_display_time
PICTURE_DURATION = args.picture_display_time
PICTURE_ISI = args.picture_isi
TEXT_DURATION = args.text_display_time
TEXT_SIZE = args.text_size
TEXT_COLOR = tuple(args.text_color)
TEXT_FONT = args.text_font
BACKGROUND_COLOR = tuple(args.background_color)
WINDOW_SIZE = tuple(args.window_size)
TOTAL_EXPE_DURATION = args.total_duration
WORD_ISI = args.rsvp_display_isi

csv_files = args.csv_files[0]

expyriment.control.defaults.window_mode=False
expyriment.control.defaults.window_mode_fullscreen=True
expyriment.control.defaults.window_size = WINDOW_SIZE
expyriment.design.defaults.experiment_background_colour = BACKGROUND_COLOR

exp = expyriment.design.Experiment(name="HiRes Experiment",
                                   background_colour=BACKGROUND_COLOR,
                                   foreground_colour=TEXT_COLOR,
                                   text_size=TEXT_SIZE,
                                   text_font=TEXT_FONT)
#expyriment.control.defaults.open_gl=1

expyriment.misc.add_fonts('fonts')

#%

expyriment.control.initialize(exp)

#exp.background_colour = BACKGROUND_COLOR
exp._screen_colour = BACKGROUND_COLOR
kb = expyriment.io.Keyboard()
bs = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
wm = stimuli.TextLine('Waiting for scanner sync (or press \'t\')',
                      text_font=TEXT_FONT,
                      text_size=TEXT_SIZE,
                      text_colour=TEXT_COLOR,
                      background_colour=BACKGROUND_COLOR)
fs = stimuli.FixCross(size=(25, 25), line_width=3, colour=TEXT_COLOR)

events = PriorityQueue()  # all stimuli will be queued here


# load stimuli

mapsounds = dict()
mapspeech = dict()
maptext = dict()
mappictures = dict()
mapvideos = dict()

for listfile in csv_files:
    stimlist = pd.read_csv(listfile)
    bp = op.dirname(listfile)

    for row in stimlist.itertuples():
        print(row)
        onset = row.onset
        stype = row.type
        f = row.stim
        try:
            cond = row.cond
        except:
            cond = ""

        if stype == 'sound':
            if not f in mapsounds:
                mapsounds[f] = stimuli.Audio(op.join(bp, f))
                mapsounds[f].preload()
            events.put((onset, cond, 'sound', f, mapsounds[f]))
        elif stype == 'picture':
            image_path = op.join(bp, f)
            if not op.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")  # Debugging
            if not f in mappictures:
                mappictures[f] = stimuli.Picture(op.join(bp, f))
                mappictures[f].scale_to_fullscreen() # Ali added - want full screen instructions
                mappictures[f].preload()

            events.put((onset, cond, 'picture', f, mappictures[f]))
            events.put((onset + PICTURE_DURATION, cond, 'blank', 'blank', bs))
        elif stype == 'video':
            if not f in mapvideos:
                mapvideos[f] = stimuli.Video(op.join(bp, f))
                mapvideos[f].preload()
            events.put((onset, cond, 'video', f, mapvideos[f]))
        elif stype == 'text':
            if not f in maptext:
                maptext[f] = stimuli.TextLine(f,
                                              text_font=TEXT_FONT,
                                              text_size=TEXT_SIZE,
                                              text_colour=TEXT_COLOR,
                                              background_colour=BACKGROUND_COLOR)
                maptext[f].preload()
            events.put((onset, cond, 'text', f, maptext[f]))
            events.put((onset + TEXT_DURATION, cond, 'blank', 'blank', bs))
        elif stype == 'rsvp':
            for i, w in enumerate(f.split(' ')):
                if not w in maptext:
                    maptext[w] = stimuli.TextLine(w,
                                                  text_font=TEXT_FONT,
                                                  text_size=TEXT_SIZE,
                                                  text_colour=TEXT_COLOR,
                                                  background_colour=BACKGROUND_COLOR)
                    maptext[w].preload()
                events.put((onset + i * (WORD_DURATION + WORD_ISI), cond, 'text', w, maptext[w]))
                if not (WORD_ISI == 0):
                    events.put((onset + i * (WORD_DURATION + WORD_ISI) + WORD_DURATION, cond, 'blank', 'blank', bs))
            if WORD_ISI == 0:
                events.put((onset + i * (WORD_DURATION + WORD_ISI) + WORD_DURATION, cond, 'blank', 'blank', bs))
        elif stype == 'pictseq':
            for i, p in enumerate(f.split(' ')):
                if not p in mappictures:
                    mappictures[p] = stimuli.Picture(op.join(bp, p))
                    mappictures[p].preload()
                events.put((onset + i * (PICTURE_DURATION + PICTURE_ISI), cond, 'picture', p, mappictures[p]))
                if not (PICTURE_ISI == 0):
                    events.put((onset + i * (PICTURE_DURATION + PICTURE_ISI) + PICTURE_DURATION, cond, 'blank', 'blank', bs))
            if PICTURE_ISI == 0:  # then erase the last picture
                events.put((onset + i * (PICTURE_DURATION + PICTURE_ISI) + PICTURE_DURATION, cond, 'blank', 'blank', bs))


exp.add_data_variable_names([ 'condition', 'time', 'stype', 'id', 'target_time'])

#%
expyriment.control.start()

if not (splash_screen is None):
    splashs = stimuli.Picture(splash_screen)
    splashs.scale_to_fullscreen()
    splashs.present()
    kb.wait_char(' ')

wm.present()
kb.wait_char('t')  # wait for scanner TTL
fs.present()  # clear screen, presenting fixation cross

a = Clock()

while not(events.empty()):
    onset, cond, stype, id, stim = events.get()
    while a.time < (onset - 10):
        a.wait(1)
        k = kb.check(keys=AUTHORIZED_KEYS)
        if k is not None:
            exp.data.add([a.time, 'button pressed,{}'.format(k)])
            
    # Present stimulus
    stim.present()
    exp.data.add(['{}'.format(cond), a.time, '{},{},{}'.format(stype, id, onset)])

    # Check for key presses
    k = kb.check(keys=AUTHORIZED_KEYS)
    if k is not None:
        exp.data.add([a.time, 'button pressed,{}'.format(k)])
        
    # Present the fixation cross
    if stype == 'blank':
        fs.present()
    
if TOTAL_EXPE_DURATION != -1:
    while a.time < TOTAL_EXPE_DURATION:
        kb.process_control_keys()
        a.wait(100)

expyriment.control.end('Merci !', 2000)
