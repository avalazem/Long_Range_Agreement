function run_visual_block(handles, block, stimuli_words, VisualTrialOrder, fid_log, triggers, cumTrial, params, events, stimuli_datasets)
Priority(MaxPriority(0));
LoadPsychHID;
Screen('Preference', 'SkipSyncTests', 0);
PsychImaging('PrepareConfiguration');

%========================================================================%
% Uniform distribution of TRs
n_TRs    =length(stimuli_words); % get the #trials
intervals=[4,6,8];               % TRs in seconds
collector={};
for interval =1:length(intervals)
    collector{interval}=transpose(repmat(intervals(interval),(n_TRs/3),1));
end
% each TR is present equal number of times
collector = horzcat(collector{:});
% permute the TRs
collector=collector(randperm(length(collector)));
%========================================================================%

%========================================================================%
% Initialize table to hold the behavioral responses.
T = cell2table(cell(length(stimuli_words),5));
T.Properties.VariableNames = {'subject_response','RT','Behavioral', 'Behavioral_index', 'TR'};
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
%%%%%%% WAIT FOR KEY PRESS

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
%======= START OF THE RSVP ==============================================%
% initialize counter to hold the correct responses
correct_responses=0;
n_trials=length(stimuli_words);

for trial=1:length(stimuli_words)
    
    PsychHID('KbQueueStart',handles.devicenum)
    PsychHID('KbQueueStart',handles.devicenumkey)
    
    
    
    %% ------------- RSVP PARAMETERS -------------------------------------%
    word_cnt       = 0;
    curr_sentence  = stimuli_words{trial};
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
    cumTrial = cumTrial+1;
    stimulus = VisualTrialOrder(trial);
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
    %WE REMOVED THE FIXATION FROM THE fMRI VERSION
    
    
    
    %% ====== PRESENT THE SENTENCES ON THE SCREEN ========================%
    %  ===================================================================%
    %  ======= START OF SENTENCE =========================================%
    for word = 1:numel(curr_sentence)
        word_cnt = word_cnt + 1;
        
        %%%%%%%%%%%%% TEXT ON %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        DrawFormattedText(handles.win, curr_sentence{word}, 'center', 'center', handles.white);
        if params.photodiode
            %[RECT presentation]
            Screen('FillRect', handles.win, handles.white, TopRightRect);
        end
        word_onset = Screen('Flip', handles.win); % Word ON
        
        %%%%%%%%%%%%%%%% ONSETS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Separate naming and trigger values based on the word position.
        if word==1
            onset_id = 'FirstStimVisualOn\t';
            if triggers;send_trigger(triggers, handles, params, events, 'first_word_onset', 0);end
        elseif word==7
            onset_id = 'LastStimVisualOn\t';
            if triggers;send_trigger(triggers, handles, params, events, 'last_word_onset', 0);end
        else
            onset_id = 'StimVisualOn\t';
            if triggers;send_trigger(triggers, handles, params, events, 'StartWord', 0);end
        end
        
        WaitSecs('UntilTime', word_onset + params.stimulus_ontime);
        
        
        % WRITE TO LOG
        fprintf(fid_log,[onset_id ...
            num2str(block) '\t' ...
            num2str(trial) '\t' ...
            num2str(stimulus) '\t' ... %
            num2str(word_cnt) '\t' ...  %
            num2str(word_onset) '\t' ...
            cond_event_name '\t' ...
            curr_sentence{word} '\t' ...
            condition '\t' ...
            structure '\t' ...
            number '\t' ...
            typ '\r\n'  ...
            ]); % write to log file
        
    end % word
    %  ======= END OF SENTENCE =========================================%
    
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
        typ '\r\n'  ...
        ]); % write to log file
    WaitSecs('UntilTime', fix2decision_onset + params.SOA_visual);
    %  ======= END OF ISI TO PANEL =====================================%
    
    
    %% ====== DECISION SCREEN ONLINE =====================================%
    % In the fMRI version, we need to keep the panel on screen for a fixed
    % period of time, unlike the M/EEG
    DrawFormattedText(handles.win, decision_screen, 'center', 'center', handles.white);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
    panel_onset= Screen('Flip', handles.win); % Pannel ON
    if triggers
        send_trigger(triggers, handles, params, events, 'StartPanel', 0)
    end
    
    % %%%%%%% WRITE TO LOG
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
        typ '\r\n'  ...
        ]); % write to log file
    
    
    %% ====== USER INPUT =====================================%
    % Different options based on the recording method. In the
    % case of the MEG, the input is provided via specific
    % MEG-compatible pads, whereas in the case of iEEG, the
    % input comes from the keyboard.
    
    if strcmp(params.method,'fMRI')
    % button response check
    [KeyIsDown, firstPress]=PsychHID('KbQueueCheck',handles.devicenum); % Collect keyboard events since KbQueueStart was invoked
            if KeyIsDown
                pressedKey=find(firstPress);
                keyname=KbName(pressedKey);
                presstimetemp=firstPress(pressedKey);
                [pTime,pInd]=sort(presstimetemp,2); % order multiple presses by press time, choose the first pressed button

                presstime=pTime(1)-RTstartTime; % for button press trials only

                    for n=1:size(pressedKey,2) % abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',handles.devicenum);
                            PsychHID('KbQueueRelease',handles.devicenum);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind-1).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
                    log(blockind-1).resp=presstime; % RT, correct for only button press blocks
                    log(blockind-1).resptime=pTime(1)-run_starttime; % resptime is correct for all blocks
                    PsychHID('KbQueueStop',handles.devicenum);                    
                end
            end
   PsychHID('KbQueueStop',handles.devicenum);
   
   [KeyIsDown2, firstPress2]=PsychHID('KbQueueCheck',handles.devicenumkey); % Collect keyboard events since KbQueueStart was invoked
            if KeyIsDown2
                pressedKey=find(firstPress2);
                keyname=KbName(pressedKey);
                presstimetemp=firstPress2(pressedKey);
                [pTime,pInd]=sort(presstimetemp,2); % order multiple presses by press time, choose the first pressed button

                presstime=pTime(1)-RTstartTime; % for button press trials only

                    for n=1:size(pressedKey,2) % abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',handles.devicenumkey);
                            PsychHID('KbQueueRelease',handles.devicenumkey);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind-1).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
                    log(blockind-1).resp=presstime; % RT, correct for only button press blocks
                    log(blockind-1).resptime=pTime(1)-run_starttime; % resptime is correct for all blocks
                    PsychHID('KbQueueStop',handles.devicenumkey);                    
                end
            end
   PsychHID('KbQueueStop',handles.devicenumkey);
        

        
        
        
        

        
    
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
    curr_TR = collector(trial);
    T.TR{trial} = curr_TR;
    
    WaitSecs('UntilTime',feed_fixation_offset + curr_TR);
    
end
%  ======= END OF TRIAL =========================================%
%% Return score to the participants:
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
    join(['_run_',num2str(block)]),...
    join(['_type_',params.block_type]),...
    '.csv']));

writetable(stimuli_datasets,curr_dataset_name,'Delimiter','\t')

