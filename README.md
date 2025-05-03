LONG-RANGE AGREEMENT
# Running the Experiment

# 1. Training
# 132 s each run, 264 s (4.4 min) total - 10 trials: 2 blocks of 5 trials/modality.
# Run 1 is Audio then Visual
# Run 2 is Visual then Audio

# Run Instructions:

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_2


# 2. Main-Exp
# 492 s each run (49.2 min total) - 2 s before first block, 2 blocks of 20 trials/modality - 12 seconds each, 10 s after final block
# Run Instructions: (Specified AUDIODRIVER for my PC - configure based on stim pc)
cd main-exp

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_2
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_3
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_4
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_5
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_6

# 3. Localizer (all have 2.0 s Merci after)
# 416 s (~7 min) total:
# Visual 222 s - 6 s before first block, 30 sec per block (30 s stim + 6 s rest), 6 s after last stim
# Audio	 194 s - 2 s before first block, 16 s per block (10 s stim + 6 rest)
# Run Instructions:
cd localizer


python runVisualCategory.py --splash visual_categories/Instructions/Instructions.png
SDL_AUDIODRIVER=alsa python audiovis.py --total-duration 194000 audio_categories/sub1_audio.csv
