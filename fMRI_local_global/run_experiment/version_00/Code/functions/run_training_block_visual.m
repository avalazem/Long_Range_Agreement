function run_training_block_visual(handles, training_words,training_dataset  ,params)
%==============================================
% YOU WON'T SEE TRIGGERS IN THE TRAINING BLOCK
%==============================================




c = onCleanup(@()sca);
Screen(handles.win,'TextSize',params.font_size);

stimuli_words=training_words;
stimuli_datasets=training_dataset;

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
    present_intro_slide(params, handles);
    wait_for_key_press()

%% Post-Instruction Pause
Screen('Flip',handles.win);
WaitSecs(2);

%========================================================================%
%======= START OF THE RSVP ==============================================%

for trial=1:length(stimuli_words)
    
    %% ------------- RSVP PARAMETERS -------------------------------------%
    word_cnt       = 0;
    curr_sentence  = stimuli_words{trial};
    curr_violIndex = stimuli_datasets.violIndex(trial);    
   
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
    
    %% -------------------------- FIXATION -------------------------------%
    %%%%%%%% DRAW FIXATION BEFORE SENTENCE (duration: params.fixation_duration)
    % This is the first fixation cross shown before the sentence appears on
    % the screen. 
    DrawFormattedText(handles.win, '+', 'center', 'center', handles.white);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw rectangle for tracker to see
    end
    fixation_onset = Screen('Flip', handles.win);

    % Keep the cross online until the first word appears. 
    WaitSecs('UntilTime',fixation_onset+params.fixation_duration_visual_block); 
    % ------------------------------------------------------------------------- %%
    
    
    
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
        WaitSecs('UntilTime', word_onset + params.stimulus_ontime);
        

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

    
    WaitSecs('UntilTime', fix2decision_onset + params.SOA_visual);
    
    %  ======= END OF ISI TO PANEL =====================================%

    
    %% ====== DECISION SCREEN ONLINE =====================================%
    DrawFormattedText(handles.win, decision_screen, 'center', 'center', handles.white);
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
    panel_onset= Screen('Flip', handles.win); % Pannel ON

    
  


    %% ====== USER INPUT =====================================%
    % Different options based on the recording method. In the 
    % case of the MEG, the input is provided via specific 
    % MEG-compatible pads, whereas in the case of iEEG, the 
    % input comes from the keyboard. 
    
    if strcmp(params.method,'MEG')
        clear Response pressed Key
        Response  = '';
        [~, firstPress] = KbQueueCheck;
        % Define the port 
        port1  = hex2dec('378');
        
        % participant should respond here now !
        Key = 0;
         while (GetSecs <= panel_onset + params.panel_ontime)
             Key  = inp(port1+1);
             if Key~=0
                 firstPress(handles.Key) = GetSecs;
%                  if triggers;send_trigger(triggers, handles, params, events, 'PressKey', 0);end
                 pressed =1;
                 break
             end
         end    
        
        % Get pad-identity and name the response direction accordingly.
        if Key==32 
            Response = 'Right';
        elseif Key==64
            Response = 'Left';
        else 
            pressed =0;
        end
        outp(888,0) 

    elseif strcmp(params.method,'ECoG')
        clear Response pressed Key
        Response  = '';
        % participant should respond here now !
         while (GetSecs <= panel_onset + params.panel_ontime)
             [pressed,press_secs,firstPress] = KbCheck;
             if pressed~=0
                 handles.Key = 3;
                 firstPress(handles.Key) = GetSecs;
%                  if triggers;send_trigger(triggers, handles, params, events, 'PressKey', 0);end
                 if firstPress(handles.RKey)
                     Response = 'Right';
                 elseif firstPress(handles.LKey)
                     Response = 'Left';
                 end        
                 break
             end
         end
    end
    
    
    if params.photodiode
        %[RECT presentation]
        Screen('FillRect', handles.win, handles.white, TopRightRect); % draw re
    end
    % ====== END OF USER INPUT =====================================%

    panel_offset    = Screen('Flip', handles.win); % Panel OFF

    % ====== END OF DECISION SCREEN ONLINE ===============================%
    
    %% ====== USER FEEDBACK ==============================================%
    if pressed
        
        if curr_violIndex == 1
            % The subjects need to choose "Wrong"
            % True-positive left side
            if strcmp(curr_wrong_location,'left') && strcmp(Response,'Left')
                T.Behavioral{trial}       = 'TP';
                % True-positive right side
            elseif strcmp(curr_wrong_location,'right') && strcmp(Response,'Right')
                T.Behavioral{trial}       = 'TP';
                % False-positive right side
            elseif strcmp(curr_wrong_location,'right') && strcmp(Response,'Left')
                T.Behavioral{trial}       = 'FN';
                % False-positive left side
            elseif strcmp(curr_wrong_location,'left') && strcmp(Response,'Right')
                T.Behavioral{trial}       = 'FN';
            end
        else
            % The subjects need to choose "OK"
            % True-negative left
            if strcmp(curr_ok_location,'left') && strcmp(Response,'Left')
                T.Behavioral{trial}       = 'TN';
                % True-negative right
            elseif strcmp(curr_ok_location,'right') && strcmp(Response,'Right')
                T.Behavioral{trial}       = 'TN';
                % False-negative left
            elseif strcmp(curr_ok_location,'left') && strcmp(Response,'Right')
                T.Behavioral{trial}       = 'FP';
                % False-negative right
            elseif strcmp(curr_ok_location,'right') && strcmp(Response,'Left')
                T.Behavioral{trial}       = 'FP';

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
        T.Behavioral{trial}       = 'NR'; % No-Response
    end
    

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
        colors = 'g';%
    elseif strcmp(T.Behavioral{trial},'FN') || strcmp(T.Behavioral{trial},'FP')
        % wrong - red cross
        color = [255,0,0];
        colors = 'r';%
    else
        % Did not press - blue cross
        color = [0,0,255];
        colors = 'b';%
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


    
    WaitSecs('UntilTime',feed_fixation_onset + params.SOA_visual);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % FEEDBACK FIXATION OFF  %%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    feed_fixation_offset = Screen('Flip', handles.win);
    
    % ====== END OF USER FEEDBACK ========================================%
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % ISI TO NEXT TRIAL     %%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    WaitSecs('UntilTime',feed_fixation_offset + params.ISI_visual);

end  
%  ======= END OF TRIAL =========================================%


