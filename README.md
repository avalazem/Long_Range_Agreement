# LONG-RANGE AGREEMENT

# CHECKLIST SUJET_XX
# - Assurez que tout fonctionne et que les câbles (en particulier pour les pressions sur le trigger et les boutons) sont branchés ☐
# - Assurez que les contrôleurs disposent de timings pour les TR et comprennent que ça attendra pour 3 "t's"  ☐
# - Assurez-vous que les boutons vrai/faux sont inversés par rapport au sujet précédent (configure in command line w/ --invert_hands, take note below !) ☐
# - Sélectionnez-en un:
#   La main droite est vraie, la gauche est fausse (normale) ☐
#   La main gauche est vraie, la droite est fausse (inverse)  ☐
# - Expliquer l'aperçu et la motivation de l'expérience à sujet ☐
# - Montrez-lui la tâche (s'il le mot était dans la phrase ou non) ☐
# - Expliquez au sujet sur quel bouton appuyer pour vrai/faux ☐
# - La pression sur le bouton est après le mot ! (pendant fixation) ☐
# - Commencez l'entraînement ☐
# - Commencez main runs ☐
# - Commencez le localisateur. ☐
# - Débriefing



# RUNNING THE EXPERIMENT
# Note: Main-Exp and Localizer wait for 3 't's

# 1. Training
# 130 s each run, 260 s (~4 min) total - 10 trials: 2 blocks of 5 trials/modality.
# Run 1 is Audio then Visual
# Run 2 is Visual then Audio

# Run Instructions:

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_1 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/training/sub_train_run_2 [--invert_hands]


# 2. Main-Exp
# 478 s (~8 min) each run, 47.8 min total
# 4 s (2 s empty 2 s cue) before first block, 2 blocks of 20 trials/modality - # 13 sec each, 10 s after final block, additional 2 sec modality cue between blocks
# Ensure differnet subjects switch left (y)/right (f) true/false order
# Run Instructions: (Specified AUDIODRIVER for my PC - configure based on stim pc)
cd main-exp

SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_1 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_2 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_3 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_4 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_5 [--invert_hands]
SDL_AUDIODRIVER=alsa python Code/long_range.py Stimuli/subject_01/sub_01_run_6 [--invert_hands]

# 3. Localizer
# 412 s (~8 min) total:
# Visual 92 s - 3 s before first block, 8.6 sec per block (0.6 stim + 8 rest)
# Audio	 320 s - 1.5 s before first block, 11.5 s per block (3.5 s stim + 6 rest)
# Run Instructions:
cd localizer/visual

python langloc-visual.py

cd ../audio

SDL_AUDIODRIVER=alsa python biling_localizer_main.py stim/long-range_localizer_sub1.csv



