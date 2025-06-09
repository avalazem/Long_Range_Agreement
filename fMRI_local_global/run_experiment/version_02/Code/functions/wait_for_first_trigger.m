function TTL=wait_for_first_trigger()


keysOfInterest_trigger=zeros(1,256);
keysOfInterest_trigger(KbName({'LeftArrow','space','RightArrow', 'ESCAPE','t'}))=1;
KbQueueCreate(-1, keysOfInterest_trigger);




PsychHID('KbQueueCreate',devicenumtrigger,keysOfInterest_trigger);
PsychHID('KbQueueCreate',devicenumkey,keysOfInterest_trigger);
PsychHID('KbQueueStart',devicenumtrigger);
PsychHID('KbQueueStart',devicenumkey);



TTL=0; % Get the TTL from the scanner
while TTL==0
    [KeyIsDown, firstPress]=PsychHID('KbQueueCheck',devicenumtrigger); % Collect keyboard events since KbQueueStart was invoked
    if KeyIsDown
        pressedKey=find(firstPress);
        keyname=KbName(pressedKey);
        presstime=firstPress(pressedKey);
        for n=1:size(pressedKey)
            if strcmp(KbName(pressedKey),trigger)==1 % TTL
                TTL=1;    % Start the experiment
                run_starttime=GetSecs;
                PsychHID('KbQueueStop',devicenumtrigger);
                PsychHID('KbQueueRelease',devicenumtrigger);
                break;
            elseif strcmp(KbName(pressedKey),esckey)==1
                exp_term=1;
                PsychHID('KbQueueStop',devicenumtrigger);
                PsychHID('KbQueueRelease',devicenumtrigger);
                break;
            else
                TTL=0;
            end
        end
    end
    
    [KeyIsDownK, firstPressK]=PsychHID('KbQueueCheck',devicenumkey); % Collect keyboard events since KbQueueStart was invoked
    if KeyIsDownK
        pressedKey=find(firstPressK);
        keyname=KbName(pressedKey);
        presstime=firstPressK(pressedKey);
        for n=1:size(pressedKey)
            if strcmp(KbName(pressedKey),trigger)==1 % TTL
                TTL=1;    % Start the experiment
                run_starttime=GetSecs;
                PsychHID('KbQueueStop',devicenumkey);
                PsychHID('KbQueueRelease',devicenumkey);
                break;
            elseif strcmp(KbName(pressedKey),esckey)==1
                exp_term=1;
                PsychHID('KbQueueStop',devicenumkey);
                PsychHID('KbQueueRelease',devicenumkey);
                break;
            else
                TTL=0;
            end
        end
    end
    if exp_term
        Priority(0);
        ShowCursor;
        Screen('CloseAll');
        TTL=-1;
        return;
    end
end

