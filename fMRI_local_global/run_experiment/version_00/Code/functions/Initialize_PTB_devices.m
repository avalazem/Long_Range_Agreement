function handles = Initialize_PTB_devices(params, handles, debug_mode)


%% AUDIO
InitializePsychSound(1);
port=0;
handles.pahandle = PsychPortAudio('Open', port, [], 2, params.freq, params.audioChannels, 1);


%% SCREEN
Screen('Preference', 'TextRenderer', 1);
screens = Screen('Screens');


handles.screenNumber = max(screens);
handles.black = BlackIndex(handles.screenNumber);
handles.white = WhiteIndex(handles.screenNumber);


rect = get(0, 'ScreenSize');
if debug_mode
    Screen('Preference', 'SkipSyncTests', 1);
    handles.rect = [0 0 rect(3:4)./2];
    handles.win = Screen('OpenWindow',handles.screenNumber, handles.black, handles.rect);
else
    Screen('Preference', 'SkipSyncTests', 0);  % REMEMBER TO HAVE THAT SET TO 0!
    handles.rect = [0 0 rect(3:4)];
    handles.win = Screen('OpenWindow',handles.screenNumber, handles.black);
end


%% TEXT ON SCREEN
Screen('TextFont',handles.win, 'Arial');
Screen('TextSize',handles.win, 120);   % 160 --> ~25mm text height (from top of `d' to bottom of `g').
Screen('TextStyle', handles.win, 1);   % 0=normal text style. 1=bold. 2=italic.

%% KEYBOARD
handles.escapeKey = KbName('ESCAPE');
handles.LKey = KbName('LeftArrow');
handles.RKey = KbName('RightArrow');
handles.Key  = KbName('space');
keysOfInterest=zeros(1,256);
keysOfInterest(KbName({'LeftArrow','space','RightArrow', 'ESCAPE'}))=1;
KbQueueCreate(-1, keysOfInterest);

























