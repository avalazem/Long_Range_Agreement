LONG-RANGE AGREEMENT
# Running the Experiment
# Note: Main-Exp and Localizer wait for 3 't's

# 1. Training
# 148 s each run, 296 s (~5 min) total - 10 trials: 2 blocks of 5 trials/modality.
# Run 1 is Audio then Visual
# Run 2 is Visual then Audio

# Run Instructions:

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_2


# 2. Main-Exp
# 538 s (~9 min) each run, 53.8 min total - 2 s before first block, 2 blocks of 20 trials/modality - # 13 sec each, 10 s after final block. 3 sec modality cue before each block.
# Ensure differnet subjects switch left (y)/right (f) true/false order
# Run Instructions: (Specified AUDIODRIVER for my PC - configure based on stim pc)
cd main-exp

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_2
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_3
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_4
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_5
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_6

# 3. Localizer
# 545 s (~9 min) total:
# Visual 95 s - 3 s before first block, 8.6 sec per block (0.6 stim + 8 rest)
# Audio	 462 s - 1.5 s before first block, 11.5 s per block (3.5 s stim + 6 rest)
# Run Instructions:
cd localizer/visual

python langloc-visual.py

cd ../audio

SDL_AUDIODRIVER=alsa python biling_localizer_main.py stim/long-range_localizer_sub1.csv



