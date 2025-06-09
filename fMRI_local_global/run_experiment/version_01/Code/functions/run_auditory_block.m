function run_auditory_block(handles, block, stimuli_words, TrialOrder, fid_log, triggers, cumTrial, params, events, stimuli_datasets)

%========================================================================%
% Initialize table to hold the behavioral responses.
T = cell2table(cell(length(stimuli_words),4));
T.Properties.VariableNames = {'subject_response','RT','Behavioral', 'Behavioral_index'};
%========================================================================%
c = onCleanup(@()sca);

Screen(handles.win,'TextSize',params.font_size);

if params.photodiode
    %---------------------------------------------------------------------%
    %--------**PHOTODIODE**-----------------------------------------------%
    %% Introduce rectangle for the Photodiode
    [screenXpixels, screenYpixels] = Screen('WindowSize', handles.win);
    % Make rectangle to present on top right for the tracker to see
    baseRect = [0 0 30 30]; % size
    xTopRight = screenXpixels * 0.95; % position
    yTopRight = screenYpixels * 0.05; % position
    TopRightRect = CenterRectOnPointd(baseRect, xTopRight, yTopRight);
    %---------------------------------------------------------------------%
end

%========================================================================%
%%%%%%% WAIT FOR KEY PRESS %%%%%%%%%%%%%%%%%%%
DrawFormattedText(handles.win, ...
    ['Partie de run: ' num2str(params.block) '/' num2str(4) newline ...
    'Cliquez sur "SPACE" pour continuer.'], ...
    'center', 'center', handles.white);
Screen('Flip',handles.win);
wait_for_key_press()


%% Post-Instruction Pause
Screen('Flip',handles.win);
WaitSecs(2);

%========================================================================%
%======= START OF THE RSAP ==============================================%
n_trials=numel(stimuli_words);
correct_responses=0;
for trial=1:length(stimuli_words)
    
    %% ------------- RSVP PARAMETERS -------------------------------------%
    curr_violIndex = stimuli_datasets.violation(trial);
    
    
    if strcmp(curr_violIndex{1},'yes')==1
        curr_violIndex=1;
    else
        curr_violIndex=0;
    end
    
    %% ------------ DECISION SCREEN SET-UP -------------------------------%
    % The words "OK" and "Wrong" will appear randomly on the screen.
    ok    = 'OK';
    wrong = 'Wrong';
    space = '     ';
    available_words = {ok, wrong};
    [word_1, idx] = datasample(available_words,1);
    available_words(idx) = [];
    word_2 = available_words;
    decision_screen   = [word_1{1},space,word_2{1}];
    
    % Locate the position of the 'OK' word in the created random panel
    idx = find(ismember(decision_screen,ok));
    if idx(1) > numel(decision_screen)/2
        curr_ok_location     = 'right';
        curr_wrong_location  = 'left';
    else
        curr_ok_location     = 'left';
        curr_wrong_location  = 'right';
    end
    % --------------------------------------------------------------------%
    
    
    
    
    
    %% ---- KEYBOARD INPUT PARAMETERS ---------------------------------- %%
    [~, ~, keyCode] = KbCheck;
    if keyCode('ESCAPE')
        DisableKeysForKbCheck([]);
        Screen('CloseAll');
        return
    end
    %cumTrial = cumTrial+1;
    stimulus = TrialOrder(trial);
    %% ----------------------------------------------------------------- %%
    
    %% ------------- UPDATE THE LOG-FILE ---------------------------------%
    %-------------------------------------------------------------------------%
    % LOG-FILE INFORMATION
    condition = stimuli_datasets(trial,:).condition{1};
    structure=stimuli_datasets(trial,:).structure{1};
    typ='visual';
    number=stimuli_datasets(trial,:).n1_number{1};
    
    cond_event_name = join([condition,'_',structure,'_',number,'_',typ]);
    %-------------------------------------------------------------------------%
    disp(['Current violation index: ' num2str(curr_violIndex)])
    fprintf('Block %i, trial %i, Condition %s, Emb %s, Number %s, Run-type %s  %s\n', ...
        block, trial, condition, structure, number, typ )
    %     WE REMOVED THE FIXATION FROM THE fMRI VERSION


    
%     %% -------------------------- FIXATION -------------------------------%
%     %%%%%%%% DRAW FIXATION BEFORE SENTENCE (duration: params.fixation_duration)
%     % This is the first fixation cross shown before the sentence appears on
%     % the screen.
%     DrawFormattedText(handles.win, '+', 'center', 'center', handles.white);
%     if params.photodiode
%         %[RECT presentation]
%         Screen('FillRect', handles.win, handles.white, TopRightRect); % draw rectangle for tracker to see
%     end
%     fixation_onset = Screen('Flip', handles.win);
%     % %%%%%%% WRITE TO LOG
%     fprintf(fid_log,['Fix\t' ...
%         num2str(block) '\t' ...
%         num2str(trial) '\t' ...
%         num2str(0) '\t' ... % Stimulus serial number in original stimulus text file
%         num2str(0) '\t' ...
%         num2str(fixation_onset) '\t' ...
%         cond_event_name '\t' ...
%         '+' '\t' ...
%         base_condition '\t' ...
%         emb '\t' ...
%         num '\t' ...
%         stimuli_datasets.block_type(trial,:) '\t' ... % blocl type (auditory or visual)
%         typ '\r\n'  ...
%         ]); % write to log file
%     
%     if triggers
%         send_trigger(triggers, handles, params, events, 'StartFixation',  0)
%     end
    [pressed, firstPress]=KbQueueCheck; % Collect keyboard events since KbQueueStart was invoked
    cumTrial=cumTrial+1;
    %     stimulus=AudioTrialOrder(trial);
    stimulus=trial;
    clear wavedata;
    wavedata(params.patientChannel,:) = stimuli_words{stimulus}(:,params.patientChannel);
    wavedata(params.TTLChannel,:)     = stimuli_words{stimulus}(:,params.patientChannel);

    % %%%%%% Echo status
    fprintf('Block %i, trial %i, stimulus %s\n', block, trial, stimuli_datasets.sentence{trial})
    % %%%%%%% Present fixation and fill buffer
    PsychPortAudio('FillBuffer', handles.pahandle, wavedata);
%     WaitSecs('UntilTime', fixation_onset + params.fixation_duration_audio_block);
    fixation_offset = Screen('Flip', handles.win);
    
    % %%%%%%% START AUDIO AND SEND TRIGGER AT START AND END
    audioOnset = PsychPortAudio('Start', handles.pahandle, 1, 0, 1); % it takes ~15ms to start the sound
    % %%%%%%% WRITE TO LOG
    fprintf(fid_log,['AudioOnset\t' ...
        num2str(block) '\t' ...
        num2str(trial) '\t' ...
        num2str(0) '\t' ... % 
        num2str(0) '\t' ...
        num2str(audioOnset) '\t' ...
        cond_event_name '\t' ...
        '+' '\t' ...
        condition '\t' ...
        structure '\t' ...
        number '\t' ...
        stimuli_datasets.block_type(trial,:) '\t' ... % block type (auditory or visual)
        typ '\r\n'  ...
        ]); % write to log file
    

    if triggers
        onset_id = 'FirstStimAuditoryOn\t';    
        send_trigger(triggers, handles, params, events, 'auditory_first_word_onset', 0)
    end

    
    
    [~, ~, ~, audioStopTime]=PsychPortAudio('Stop', handles.pahandle,1);
    % %%%%%%% WRITE TO LOG
    fprintf(fid_log,['AudioOffset\t' ...
        num2str(block) '\t' ...
        num2str(trial) '\t' ...
        num2str(0) '\t' ... % 
        num2str(0) '\t' ...
        num2str(audioStopTime) '\t' ...
        cond_event_name '\t' ...
        '+' '\t' ...
        condition '\t' ...
        structure '\t' ...
        number '\t' ...
        stimuli_datasets.block_type(trial,:) '\t' ... % block type (auditory or visual)
        typ '\r\n'  ...
        ]); % write to log file
    
    if triggers
        onset_id = 'LastStimAuditoryOn\t';
        send_trigger(triggers, handles, params, events, 'auditory_last_word_ofset', 0)
    end
    
    % %%%%%%% CLEAR-UP (buffer and screen)
    PsychPortAudio('DeleteBuffer',[],1); % clear the buffer
    

    % ======= END OF SENTENCE =========================================%
    
    %% ====== ISI TO PANEL ===============================================%
    %  ======= START OF ISI TO PANEL =====================================%
    DrawFormattedText(handles.win, '+', 'center', 'center', [255,255,255]);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw rectangle for tracker to see
    end
    fix2decision_onset  = Screen('Flip', handles.win);
    if triggers
        send_trigger(triggers, handles, params, events, 'StartFix2Decision', 0)
    end
    
    % %%%%%%% WRITE TO LOG
    fprintf(fid_log,['Fix2DecisionON\t' ...
        num2str(block) '\t' ...
        num2str(trial) '\t' ...
        num2str(0) '\t' ... % 
        num2str(0) '\t' ...
        num2str(fix2decision_onset) '\t' ...
        cond_event_name '\t' ...
        '+' '\t' ...
        condition '\t' ...
        structure '\t' ...
        number '\t' ...
        stimuli_datasets.block_type(trial,:) '\t' ... % block type (auditory or visual)
        typ '\r\n'  ...
        ]); % write to log file
    WaitSecs('UntilTime', fix2decision_onset + params.SOA_visual);
    
    %  ======= END OF ISI TO PANEL =====================================%

    
    %% ====== DECISION SCREEN ONLINE =====================================%
    DrawFormattedText(handles.win, decision_screen, 'center', 'center', handles.white);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
    panel_onset= Screen('Flip', handles.win); % Pannel ON
    if triggers
        send_trigger(triggers, handles, params, events, 'StartPanel', 0)
    end
    
    %%%%%%%% WRITE TO LOG
    fprintf(fid_log,['PanelOn\t' ...
        num2str(block) '\t' ...
        num2str(trial) '\t' ...
        num2str(0) '\t' ... % 
        num2str(0) '\t' ...
        num2str(panel_onset) '\t' ...
        cond_event_name '\t' ...
        'Panel' '\t' ...
        condition '\t' ...
        structure '\t' ...
        number '\t' ...
        stimuli_datasets.block_type(trial,:) '\t' ... % blocl type (auditory or visual)
        typ '\r\n'  ...
        ]); % write to log file


    %% ====== USER INPUT =====================================%
    % Different options based on the recording method. In the 
    % case of the MEG, the input is provided via specific 
    % MEG-compatible pads, whereas in the case of iEEG, the 
    % input comes from the keyboard. 
    
    
    clear Response pressed Key
    Response  = '';
    % participant should respond here now !
    while (GetSecs <= panel_onset + params.panel_ontime)
        [pressed,press_secs,firstPress] = KbCheck;
        if pressed~=0
            handles.Key = 3;
            firstPress(handles.Key) = GetSecs;
            if firstPress(handles.RKey)
                Response = 'Right';
            elseif firstPress(handles.LKey)
                Response = 'Left';
            end
            break
        end
    end
    
        
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
        % ====== END OF USER INPUT =====================================%
    % add a waiting factor here so the panel stays on for the desired
    % duration
    RT=num2str(firstPress(handles.Key)- panel_onset);
    if firstPress(handles.Key)==0
        time2wait=params.max_RT;
    else
        time2wait=params.max_RT-str2double(RT);
    end
    
    WaitSecs('UntilTime', time2wait);
    panel_offset    = Screen('Flip', handles.win); % Panel OFF
    
    % ====== END OF DECISION SCREEN ONLINE ===============================%
    
    %% ====== USER FEEDBACK ==============================================%
    if pressed
        %%%%%%%%%%%%%%%%%
        % LOG-FILES %%%%
        %%%%%%%%%%%%%%%%%
        fprintf(fid_log,['KeyPress\t' ...
            num2str(block) '\t' ...
            num2str(trial) '\t' ...
            num2str(press_secs-panel_onset) '\t' ... % 
            num2str(0) '\t' ...   %
            num2str(firstPress(handles.Key)) '\t' ...
            cond_event_name '\t' ...
            Response '\t' ...  %
            condition '\t' ...
            structure '\t' ...
            number '\t' ...
            typ '\r\n'  ...
            ]); % write to log file
        
        
        % ======== UPDATE THE LOG FILES BASED ON THE USER'S RESPONSE ===%
        % In the following lines of code, the Log-files are updated based
        % on the location of the words "OK" and "Wrong" (see section 
        % 'Decision screen setup') and the key that the subject pressed. 
        % This section is essential for the behavioral performance part of
        % the project as it procides with the measures of True-Positives 
        % (TP), True-Negatives (TN) etc as well as with the Reaction-times.
        
        if curr_violIndex == 1
            % The subjects need to choose "Wrong"
            % True-positive left side
            if strcmp(curr_wrong_location,'left') && strcmp(Response,'Left')
                T.subject_response{trial} = 1;
                T.RT{trial}               = num2str(firstPress(handles.Key)- panel_onset);
                T.Behavioral{trial}       = 'TP';
                T.Behavioral_index{trial} = 1;
                % True-positive right side
            elseif strcmp(curr_wrong_location,'right') && strcmp(Response,'Right')
                T.subject_response{trial} = 1;
                T.RT{trial}               = num2str(firstPress(handles.Key)- panel_onset);
                T.Behavioral{trial}       = 'TP';
                T.Behavioral_index{trial} = 1;
                % False-positive right side
            elseif strcmp(curr_wrong_location,'right') && strcmp(Response,'Left')
                T.subject_response{trial} = 0;
                T.RT{trial}               = num2str(firstPress(handles.Key)- panel_onset);
                T.Behavioral{trial}       = 'FN';
                T.Behavioral_index{trial} = 2;
                % False-positive left side
            elseif strcmp(curr_wrong_location,'left') && strcmp(Response,'Right')
                T.subject_response{trial} = 0;
                T.RT{trial}               = num2str(firstPress(handles.Key)- panel_onset);
                T.Behavioral{trial}       = 'FN';
                T.Behavioral_index{trial} = 2;
            end
        else
            % The subjects need to choose "OK"
            % True-negative left
            if strcmp(curr_ok_location,'left') && strcmp(Response,'Left')
                T.subject_response{trial} = 0;
                T.RT{trial}               = num2str(firstPress(handles.Key)-panel_onset);
                T.Behavioral{trial}       = 'TN';
                T.Behavioral_index{trial} = 3;
                % True-negative right
            elseif strcmp(curr_ok_location,'right') && strcmp(Response,'Right')
                T.subject_response{trial} = 0;
                T.RT{trial}               = num2str(firstPress(handles.Key)-panel_onset);
                T.Behavioral{trial}       = 'TN';
                T.Behavioral_index{trial} = 3;
                % False-negative left
            elseif strcmp(curr_ok_location,'left') && strcmp(Response,'Right')
                T.subject_response{trial} = 1;
                T.RT{trial}               = num2str(firstPress(handles.Key)-panel_onset);
                T.Behavioral{trial}       = 'FP';
                T.Behavioral_index{trial} = 4;
                % False-negative right
            elseif strcmp(curr_ok_location,'right') && strcmp(Response,'Left')
                T.subject_response{trial} = 1;
                T.RT{trial}               = num2str(firstPress(handles.Key)-panel_onset);
                T.Behavioral{trial}       = 'FP';
                T.Behavioral_index{trial} = 4;
            end
        end
        
        
        %%%%%%%%%%%%%%%%%
        % ESCAPE-KEY %%%%
        %%%%%%%%%%%%%%%%%
        if firstPress(KbName('escape'))
            error('Escape key was pressed')
        end
    else
        % The subject did not press anything
        T.subject_response{trial} = NaN;
        T.RT{trial}               = NaN;
        T.Behavioral{trial}       = 'NR'; % No-Response
        T.Behavioral_index{trial} = 5;
    end
    
    % check RT values
    if str2double(T.RT{trial})<0 || str2double(T.RT{trial}) > panel_offset
        T.RT{trial} = NaN;
    end
    disp(T.RT{trial})
    % ===== END OF LOG UPDATE BASED ON THE USER'S RESPONSE ===============%
    
    %--------------------------------------%
    %############# FEEDBACK ###############%
    % Use the behavioral index for feedback:
    %--------------------------------------%
    if strcmp(T.Behavioral{trial},'TN') || strcmp(T.Behavioral{trial},'TP')
        % correct - green cross
        % Change the color of the fixation cross depending on the subject's
        % performance.
        color = [0,255,0];
        correct_responses=correct_responses+1;
    elseif strcmp(T.Behavioral{trial},'FN') || strcmp(T.Behavioral{trial},'FP')
        % wrong - red cross
        color = [255,0,0];
    else
        % Did not press - blue cross
        color = [0,0,255];
    end
    
    
    % -------------------------- FEEDBACK FIXATION ----------------------------------- %%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % FEEDBACK FIXATION ON  %%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    DrawFormattedText(handles.win, '+', 'center', 'center', color);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
    feed_fixation_onset = Screen('Flip', handles.win);
    if triggers
        send_trigger(triggers, handles, params, events, 'StartFixFeedback', 0)
    end
    %%%%%%%% WRITE TO LOG
    fprintf(fid_log,['FixFeedbackOn\t' ...
        num2str(block) '\t' ...
        num2str(trial) '\t' ...
        num2str(0) '\t' ... 
        num2str(0) '\t' ...
        num2str(feed_fixation_onset) '\t' ...
        cond_event_name '\t' ...
        T.Behavioral{trial} '\t' ...
        condition '\t' ...
        structure '\t' ...
        number '\t' ...
        typ '\r\n'  ...
        ]); % write to log file
    
    
    WaitSecs('UntilTime',feed_fixation_onset + params.SOA_visual);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % FEEDBACK FIXATION OFF  %%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    feed_fixation_offset = Screen('Flip', handles.win);
    
    % ====== END OF USER FEEDBACK ========================================%
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % ISI TO NEXT TRIAL     %%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % This should be jittered
    jitter_pool=[4,6,8];
    jittered_window = datasample(jitter_pool,1);

    WaitSecs('UntilTime',feed_fixation_offset + jittered_window);
    

end  
%  ======= END OF TRIAL =========================================%

correct=(correct_responses/n_trials)*1e2;
DrawFormattedText(handles.win, ...
    ['You scorred: ' num2str(round(correct)) '%' newline ...
    'Press "SPACE" to continue.'], ...
    'center', 'center', handles.white);
Screen('Flip',handles.win);
wait_for_key_press()

if correct>70
    present_feedback_slide(params, handles);
    wait_for_key_press()
end
    






%% ====== UPDATE & SAVE THE BEHAVIORAL PERFORMANCE =======================%

% Concatenate the datasets for the current block:
path2output = fullfile('..','Behavioral',params.method, ...
    join(['subj_',params.sub_code]));
if ~exist(path2output , 'dir')
    mkdir(path2output )
end
% append to the dataset
stimuli_datasets = ...
    [stimuli_datasets,T ];
% export to Output
curr_dataset_name = fullfile(path2output, ...
    join([params.method, ...
    join(['_subj_',params.sub_code]), ...
    join(['_block_',num2str(block)]),...
    '.csv']));

writetable(stimuli_datasets,curr_dataset_name,'Delimiter','\t')
    
end




















