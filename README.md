LONG-RANGE AGREEMENT
# Running the Experiment

# 1. Training
# 264 s (4.4 min) total - 132 s each. 10 trials: 2 blocks of 5 trials/modality

# Run Instructions:

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_2


# 2. Main-Exp
# 492 s each run (49.2 min total) - 2 s before first block, 2 blocks of 20 trials/modality - 12 seconds each, 10 s after final block
# Run Instructions:
cd main-exp

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_2
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_3
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_4
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_5
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_6

# 3. Localizer (all have 2.0 s Merci after)
# 607 s (10.12 min) total:
# Visual 222 s - 6 s before first block, 30 sec per block (30 s stim + 6 s rest), 6 s after last stim
# Audio	 194 s - 2 s before first block, 16 s per block (10 s stim + 6 rest)
# Speech 191 s - 3 s before first, 10 s per block, 6 s rest after
# Run Instructions:
cd localizer


python runVisualCategory.py --splash visual_categories/Instructions/Instructions.png
python audiovis.py --total-duration 194000 audio_categories/sub1_audio.csv python audiovis.py --splash hand_categories/Instructions.png --total-duration 191000 hand_categories/sub1_hand.csv python audiovis.py --splash speech_categories/Instructions.png --total-duration 191000 speech_categories/sub1_speech.csv
