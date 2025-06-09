%% Language-local-global paradigm.
% @UNICOG,NEUROSPIN-2k19
% ------------------------------------------------
rng('default')
clear; close all; clc
Screen('CloseAll');
PsychPortAudio('Close');
% ------------------------------------------------
commandwindow;

%% MODE SELECTION
%#################################################################
debug_mode = 0;
if debug_mode
    dbstop if error
    training = 1;
else
    training = questdlg('Do you want to include a training block?','Training block','Yes','No','Yes');
    if training(1) == 'Y', training = 1; else training = 0; end
    %     training = 0;
end
%#################################################################

%% INITIALIZATION (parameters)
%#################################################################
addpath('functions')
KbName('UnifyKeyNames')
[params, events] = getParamsLocalGlobalParadigm(debug_mode);

% TTL settings
params.location ='NeuroSpin';  %options: 'Houston' or 'NeuroSpin', affecting hardware to use for TTLs
params.portA    = 1;
params.portB    = 0;

% Running on PTB-3? Abort otherwise.
AssertOpenGL;
%#################################################################

%% TRIGGERS
%#################################################################
% Send TTLs though the DAQ hardware interface
% triggers = questdlg('Send TTLs?','TTLs status','Yes (recording session)','No (just playing)','Yes (recording session)');
triggers = 0;
if triggers(1) == 'Y', triggers = 1; else triggers = 0; end
% if ~triggers, uiwait(msgbox('TTLs  will  *NOT*  be  sent - are you sure you want to continue?','TTLs','modal')); end
%################################################################

%% HANDLES
%#################################################################
handles = initialize_TTL_hardware(triggers, params, events);
%#################################################################

%% LOAD LOG, STIMULI, PTB handles.
%#################################################################
fid_log = createLogFileLocalGlobalParadigm(params); % OPEN LOG
%% LOAD STIMULI
[stimuli_words, stimuli_datasets, training_words, training_dataset] = load_stimuliLocalGlobal(params);
% Open screens
handles = Initialize_PTB_devices(params, handles, debug_mode);
warning off;
block = params.block;
%#################################################################
%% START EXPERIMENT
%#################################################################
c = onCleanup(@()sca);

try


    % --- TRAINING TRIALS  ----------------------------------------------
    if training
        % Split based on the type of the Block
        if strcmp(params.block_type, 'visual')
            run_training_block_visual(handles, training_words, training_dataset, params);
            PsychPortAudio('Close');
            handles = Initialize_PTB_devices(params, handles, debug_mode);
        elseif strcmp(params.block_type, 'auditory')
            run_training_auditory_block(handles, 0, training_words, ...
            0, fid_log, triggers, 0, ...
            params, events, training_dataset)
            PsychPortAudio('Close');
            handles = Initialize_PTB_devices(params, handles, debug_mode);
        end
    end
    

    % --------------------------------------------------------------------
    % PRESENT LONG FIXATION ONLY AT THE BEGINING
    Screen(handles.win,'TextSize',params.font_size);
    DrawFormattedText(handles.win, '+', 'center', 'center', handles.white);
    Screen('Flip', handles.win);
    WaitSecs(1.5); %Wait before experiment start
    % --------------------------------------------------------------------
    
    
    % %%%%%%% RANDOMIZE TRIAL LIST %%%%%%%%
    TrialOrder=randperm(length(stimuli_words));
    
    % --- STIMULI PRESENTATION  --------------------------------------
    if strcmp(params.block_type, 'visual')
        % --- VISUAL STIMULI --------------------------------------
        run_visual_block(handles, block, stimuli_words, ...
            TrialOrder, fid_log, triggers, 0, ...
            params, events, stimuli_datasets);
        Screen('CloseAll');
        PsychPortAudio('Close');
        % -----------------------------------------------------------------
    elseif strcmp(params.block_type, 'auditory')
        % --- AUDITORY STIMULI  --------------------------------------
        run_auditory_block(handles, block, stimuli_words, ...
            TrialOrder, fid_log, triggers, 0, ...
            params, events, stimuli_datasets);
        Screen('CloseAll');
        PsychPortAudio('Close');
        % -----------------------------------------------------------------
    end
    
    % -----------------------------------------------------------------
catch
    sca
    psychrethrow(psychlasterror);
    KbQueueRelease;
    fprintf('Error occured\n')
end

%% %%%%%%% CLOSE ALL - END EXPERIMENT
fprintf('Done\n')
KbQueueRelease;
sca
