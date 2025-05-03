LONG-RANGE AGREEMENT
# Running the Experiment

# 1. Training
# 264 s (4.4 min) total, 132 s each. 10 trials: 2 blocks of 5 trials/modality

# Run Instructions:

python Code/long_range.py Stimuli/training/sub_train_run_1
python Code/long_range.py Stimuli/training/sub_train_run_2


# 2. Main-Exp
# 492 s each run; 49.2 min total - 2 s before first block, 2 blocks of 20 trials/modality - 12 seconds each, 10 s after final block
# Run Instructions:
cd main-exp

python Code/long_range.py Stimuli/subject_01/sub_01_run_1
python Code/long_range.py Stimuli/subject_01/sub_01_run_2
python Code/long_range.py Stimuli/subject_01/sub_01_run_3
python Code/long_range.py Stimuli/subject_01/sub_01_run_4
python Code/long_range.py Stimuli/subject_01/sub_01_run_5
python Code/long_range.py Stimuli/subject_01/sub_01_run_6

# 3. Localizer (all have 1.5s Merci after)
# Visual 260 s - 6 s before first block, 14 sec per block (8 =20*0.4 s stim + 6 s rest), 8 s after last stim
# Audio	 196 s - 2 s before first block, 16 s per block (10 s stim + 6 rest), 2 s after last stim
# Speech 191 s - 3 s before first, 10 s per block, 6 s rest after, 2 after last stim

# Run Instructions:
cd localizer

python runVisualCategory.py
python audiovis.py --total-duration 196000 audio_categories/sub1_audio.csv
python audiovis.py --splash speech_categories/instructions.png --total-duration 191000 speech_categories/sub1_speech.csv
