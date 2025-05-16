LONG-RANGE AGREEMENT
# Running the Experiment
# Note: Main-Exp and Localizer wait for 3 't's

# 1. Training
# 130 s each run, 260 s (~4 min) total - 10 trials: 2 blocks of 5 trials/modality.
# Run 1 is Audio then Visual
# Run 2 is Visual then Audio

# Run Instructions:

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_1
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_2


# 2. Main-Exp
# 478 s (~8 min) each run, 47.8 min total
# 4 s (2 s empty 2 s cue) before first block, 2 blocks of 20 trials/modality - # 13 sec each, 10 s after final block, additional 2 sec modality cue between blocks
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
# 415 s (~8 min) total:
# Visual 95 s - 3 s before first block, 8.6 sec per block (0.6 stim + 8 rest)
# Audio	 320 s - 1.5 s before first block, 11.5 s per block (3.5 s stim + 6 rest)
# Run Instructions:
cd localizer/visual

python langloc-visual.py

cd ../audio

SDL_AUDIODRIVER=alsa python biling_localizer_main.py stim/long-range_localizer_sub1.csv



