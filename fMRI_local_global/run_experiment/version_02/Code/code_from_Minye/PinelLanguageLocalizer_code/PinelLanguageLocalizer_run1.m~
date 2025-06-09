% Pinel Localizer. visual & auditory 
% Version 20190904

% stimuli categories=10; reordered category indices:
% 1=checkerH; 2=checkerV; 3=buttonL_a; 4=buttonR_a; 5=buttonL_v; 6=buttonR_v; 
% 7=calculation_a; 8=calculation_v; 9=phrase_a; 10=phrase_v;
% aud conds: 3,4,7,9
% vis conds: 1,2,5,6,8,10

% central presentation; 6s fixation at the start/end of the run
% buttons:
% Press esc to exit. 
% 10 repetitions per condition for 1,2,7,8,9,10; 5 repetitions for 3,4,5,6; 
% Button press recording using PsychHID, KbQueueCheck. 
% log by blocks. 
% response time computed upon block onset. 
% fixation cross not present during word presentation
% 4 lists for calc and phrases. Randomly select a list separately for the two

% code logic:
% Fixed (pseudorandomized): list of conditions & timing 
% Random: calc & phrase lists. 
% stim presented by the fixed timing
 
% Screen resolution=1920x1080; screen size=69.84 cm; screen distance=195 cm;
% font size=66;
% button boxes keys=b,y; scanner trigger=t;

% Specific to matlab toolboxes: replaced functions in the statistics toolbox 
% with the ones in psychtoolbox: randperm->NRandPerm; randsample->URandSel;


clear;
subjno=input('Please input date (YYYYMMDD):', 's');
subjname=input('Please input subject number:', 's');
% load('subjCatLocalizer.mat');

runnum=1;


AssertOpenGL;
KbName('UnifyKeyNames');
%% trial timing definition
numblocks=80; % total number of blocks per run

stimdur=0.25; % letter string presentation time
fixdur=0.1; % ITI between letter strings
checkerdur=0.2; % checker presentation time

% fixini=6; % initial fixation period
fixini=6;
fixend=6; % fixation period at the end of the run

% lettershift=2; % stimuli presentation, number of letters away from the fixation dot (1 or 2)
rendershift=4; % in pixels, specific for text renderer 1. 
stimfont='Arial';
instructfont='Arial';

listlength=4; % number of strings per list

distance=195;% temporary
screenwid=69.84; % temporary
screenpx=1920; % temporary
% theta=atan(stimwidth/2/distance)*180/pi*2;

% contents of the instruction screen, modify here. 
textstart='Waiting for the scanner trigger'; % lower line
textinstruct='Please fixate on the fixation cross throughout the experiment'; % upper line

% check FORP key devices and get device indices
clear PsychHID; 
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices;
[logicalTrig,locationTrig]=ismember({'Current Designs, Inc. TRIGI-USB'},productNames);% trigger device
[logicalButt,locationButt]=ismember({'Arduino LLC Arduino Leonardo'},productNames);% 2-button device
[logicalKey,locationKey]=ismember({'Dell Dell USB Keyboard'},productNames);% PC keyboard

devicenumtrigger=allInfos{locationTrig}.index;
devicenum=allInfos{locationButt}.index;
devicenumkey=allInfos{locationKey}.index;

% for windows
% devicenumtrigger=-1;%temporary
% devicenum=-1;
% devicenumkey=-1;

% define the corresponding keys of the button box here
% use KbName('KeyNames') to check the key correspondence in the current system
trigger='t'; % scanner trigger key value
esckey='ESCAPE'; % escape key
spacekey='space'; % space key
button1='b'; % MR response buttons
button2='y';
button3='g';
button4='r';
button5='m';

% mapping response buttons defined above. 
% here, b, y, g, r, ,< mapped to value 1-5;
keysOfInterestResp=zeros(1,256);
keysResp={esckey,button1,button2,button3,button4,button5}; 
keysOfInterestResp(KbName(keysResp))=1;
keycodemapping=zeros(1,256);
keycodemappingind=zeros(1,length(keysResp)-1);

for kmind=2:length(keysResp)
    keycodemappingind(kmind-1)=KbName(keysResp{kmind});
    keycodemapping(KbName(keysResp{kmind}))=kmind-1;
end


% stimsize=ceil(22/640*screenpx); % font size
stimsize=48;
stimcolor=[255 255 255];
BGcolor=[0 0 0];
fixcolor=[255 255 255]; % category localizer: [26 167 19];
% fixsize=7/640*screenpx;
instructsize=30;
fixwidth=48;
fixthick=4;

dirdata=pwd;
resultfolder=sprintf('%s_%s',subjno,subjname);

% audio device setup
freq=22050;
channels=2;
volume=1;

clear PsychPortAudio;
audiodevices=PsychPortAudio('GetDevices');
audiodevicenames={audiodevices.DeviceName};
% [logicalaudio,locationaudio]=ismember({'Aureon5.1MkII: USB Audio (hw:2,0)'},audiodevicenames);
[logicalaudio,locationaudio]=ismember({'Realtek ASIO'},audiodevicenames); % temporary
% audiodeviceindex=audiodevices(locationaudio).DeviceIndex;% temporary
audiodeviceindex=-1;

%% load stim list file (cells of strings)
% Randomize during the exp: block order
load('stimlistall_PinelLanguage.mat');% 84 stim lists
load('checker_PinelLanguage.mat'); % checkerboard
load('condtiming_PinelLanguage.mat'); % fixed conditions & onsets

% Set the rand method
rng('shuffle'); % octave specific, turn off; 

% Block randomization: 
% randomly select 4 lists:
% one calc_v (1:40), one phrase_v (41:80), one calc_a (85:124), one
% phrase_a (125:164)
calcphrlist=[reshape(1:80,[10 8]),reshape(85:164,[10,8])];
calcphrlistselect=calcphrlist(:,[URandSel(1:4,1) URandSel(5:8,1) URandSel(9:12,1) URandSel(13:16,1)]);
% calcphrlistselect=reshape(calcphrlistselect,[10,4]);
calcphrlistselectfin(:,1)=calcphrlistselect(NRandPerm(10,10),1);
calcphrlistselectfin(:,2)=calcphrlistselect(NRandPerm(10,10),2);
calcphrlistselectfin(:,3)=calcphrlistselect(NRandPerm(10,10),3);
calcphrlistselectfin(:,4)=calcphrlistselect(NRandPerm(10,10),4);


%% add trial info, randomized oddball info to log file
log(numblocks).ind=[];
log(1).cat=[];
log(1).type=[];
log(1).list=[];
log(1).onset=[];
log(1).resp=[];
log(1).resptime=[];
log(1).key=[];
log(1).SDT=[]; % 0.3<resp<1.3: 1=hit; otherwise: 2=miss;
log(1).blockstart=[];
log(1).content=[];


indcalc_v=1;
indphr_v=1; 
indcalc_a=1;
indphr_a=1; % for adding calc & phrase conditions
for blockind=1:numblocks
%    tempID=currentrunassign(blockorder(blockind));
   cattemp=condtiming(blockind,1);
   log(blockind).cat=cattemp;
   log(blockind).onset=condtiming(blockind,2);
   
       if cattemp==1
           tempID=83;           
       elseif cattemp==2
           tempID=84;
       elseif cattemp==3
           tempID=165;
       elseif cattemp==4
           tempID=166;
       elseif cattemp==5
           tempID=81;
       elseif cattemp==6
           tempID=82;
       elseif cattemp==7
           tempID=calcphrlistselectfin(indcalc_a,3);
           indcalc_a=indcalc_a+1;
       elseif cattemp==8
           tempID=calcphrlistselectfin(indcalc_v,1);
           indcalc_v=indcalc_v+1;
       elseif cattemp==9
           tempID=calcphrlistselectfin(indphr_a,4);
           indphr_a=indphr_a+1;   
       else
           tempID=calcphrlistselectfin(indphr_v,2);
           indphr_v=indphr_v+1;
       end
   log(blockind).ind=tempID;
   log(blockind).type=stimlistall(tempID).type;
   log(blockind).list=stimlistall(tempID).list;
   log(blockind).content=stimlistall(tempID).content; 

end 

%% display trials
try 
  Priority(MaxPriority(0));
  LoadPsychHID;
  InitializePsychSound;
  Screen('Preference', 'SkipSyncTests', 0);
  PsychImaging('PrepareConfiguration');
  [w,rect]=PsychImaging('OpenWindow',0,BGcolor); 
  Screen('BlendFunction',w,GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
  Screen('Preference', 'DefaultFontSize', instructsize);
  Screen('Preference', 'DefaultFontStyle',0);
  Screen('Preference', 'TextRenderer',1);
  Screen('Preference','DefaultFontName',stimfont);
  Screen('Preference', 'VisualDebugLevel', 3);
  HideCursor;
  pahandle = PsychPortAudio('Open',audiodeviceindex, [], 0, freq, channels);
  PsychPortAudio('Volume', pahandle, volume);
% window size
  sxsize=rect(3);
  sysize=rect(4);
  cx=sxsize/2;
  cy=sysize/2;
  
  fixrects=[cx-fixwidth/2     cx-fixthick/2;
            cy-fixthick/2     cy-fixwidth/2;
            cx+fixwidth/2     cx+fixthick/2;
            cy+fixthick/2     cy+fixwidth/2]; % fixation cross
  ovalrects=[cx-fixwidth/2; cy-fixwidth/2; cx+fixwidth/2; cy+fixwidth/2]; % fixation point
        
  hz=Screen('FrameRate',w);
  ifi=Screen('GetFlipInterval',w,100);
  exp_term=0;
  stimflipnum=stimdur/ifi-0.5;
  checkerflipnum=checkerdur/ifi-0.5;
  fixflipnum=fixdur/ifi-0.5;
 


  % Instruction screen
  Screen('TextSize',w,instructsize);
  Screen('TextFont',w,instructfont);
  wtinstruct=RectWidth(Screen('TextBounds',w,textinstruct));
  htinstruct=RectHeight(Screen('TextBounds',w,textinstruct));
  wtstart=RectWidth(Screen('TextBounds',w,textstart));
  htstart=RectHeight(Screen('TextBounds',w,textstart));
  Screen('DrawText',w,textinstruct,cx-wtinstruct/2,cy-htinstruct/2-30,stimcolor)
  Screen('DrawText',w,textstart,cx-wtstart/2,cy-htstart/2+30,stimcolor)
  
  Screen('Flip',w);  

  
keysOfInterest=zeros(1,256);
keysOfInterest(KbName({spacekey,esckey,trigger}))=1;
PsychHID('KbQueueCreate',devicenumtrigger,keysOfInterest);
% PsychHID('KbQueueCreate',devicenumkey,keysOfInterest);
PsychHID('KbQueueStart',devicenumtrigger);
% PsychHID('KbQueueStart',devicenumkey);


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
        
%         [KeyIsDownK, firstPressK]=PsychHID('KbQueueCheck',devicenumkey); % Collect keyboard events since KbQueueStart was invoked
%         if KeyIsDownK
%             pressedKey=find(firstPressK);
%             keyname=KbName(pressedKey);
%             presstime=firstPressK(pressedKey);
%             for n=1:size(pressedKey)
%                 if strcmp(KbName(pressedKey),trigger)==1 % TTL
%                     TTL=1;    % Start the experiment
%                     run_starttime=GetSecs;
%                     PsychHID('KbQueueStop',devicenumkey);
%                     PsychHID('KbQueueRelease',devicenumkey);
%                     break;
%                 elseif strcmp(KbName(pressedKey),esckey)==1
%                     exp_term=1;
%                     PsychHID('KbQueueStop',devicenumkey);
%                     PsychHID('KbQueueRelease',devicenumkey);                   
%                     break;
%                 else
%                     TTL=0;
%                 end
%             end          
%         end
        if exp_term
            Priority(0);
            ShowCursor;
            Screen('CloseAll');
            return;
        end
    end


% fixation (start)

Screen('FillRect',w,fixcolor,fixrects);
Screen('Flip',w);

WaitSecs(fixini); % starting fixation 
% WaitSecs(1); % for debugging


PsychHID('KbQueueCreate',devicenum,keysOfInterestResp);    
% PsychHID('KbQueueCreate',devicenumkey,keysOfInterestResp);    

% % pre-set the text box to save computation time
textstim='l';
Screen('TextFont',w,stimfont);
Screen('TextSize',w,stimsize);
Screen('TextStyle',w,0);
% wtstim=RectWidth(Screen('TextBounds',w,textstim));
htstim=RectHeight(Screen('TextBounds',w,textstim));
% textoneletter='A';
% widthoneletter=RectWidth(Screen('TextBounds',w,textoneletter));
% 
% xposition=floor(cx-wtstim/2-rendershift);


% block loop
for blockind=1:numblocks
stimblock=log(blockind).content;
    
 PsychHID('KbQueueStart',devicenum)
 PsychHID('KbQueueStart',devicenumkey)
 TstartTime=GetSecs;  
 vbl=log(blockind).onset+fixini+run_starttime;
 Screen('FillRect',w,fixcolor,fixrects);
 vbl=Screen('Flip',w,vbl);
 respstart=vbl;
 log(blockind).blockstart=vbl-run_starttime;
 
 if log(blockind).cat==3||log(blockind).cat==4||log(blockind).cat==5||log(blockind).cat==6
     RTstartTime=GetSecs;
 end

     if log(blockind).cat==1||log(blockind).cat==2 % checkers
         for stimind=1:8
             %         picstim=matlab.lang.makeValidName(stimblock{stimind,1});
             picstim=Screen('MakeTexture',w,checker(stimblock{stimind}).img);
             stimwd=size(checker(stimblock{stimind}).img,2);
             stimht=size(checker(stimblock{stimind}).img,1);
             Screen('DrawTexture',w,picstim,[],[cx-stimwd/2 cy-stimht/2 cx+stimwd/2 cy+stimht/2]);
%              Screen('FillRect',w,fixcolor,fixrects);

             Screen('Flip',w,vbl);
             vbl=vbl+checkerflipnum*ifi;


             Screen('Close',picstim);
         end
             Screen('FillRect',w,fixcolor,fixrects);
             vbl=Screen('Flip',w);
     elseif log(blockind).cat==3||log(blockind).cat==4||log(blockind).cat==7||log(blockind).cat==9
         % auditory block
             Screen('FillRect',w,fixcolor,fixrects);
             vbl=Screen('Flip',w);
             audiodata=repmat(stimblock,2,1);
             PsychPortAudio('FillBuffer', pahandle, audiodata);
             PsychPortAudio('Start',pahandle,1);
     else % string block
         for stimind=1:listlength
             textstim=stimblock{stimind};
             
             Screen('TextFont',w,stimfont);
             Screen('TextSize',w,stimsize);
             Screen('TextStyle',w,0);
             wtstim=RectWidth(Screen('TextBounds',w,textstim));
%              htstim=RectHeight(Screen('TextBounds',w,textstim));
             
             Screen('DrawText',w,textstim,cx-wtstim/2,cy+htstim/2,stimcolor,[],1);
             
             vbl=Screen('Flip',w);
             log(blockind).content{stimind,2}=GetSecs-run_starttime;

             Screen('FillRect',w,fixcolor,fixrects);
             vbl=Screen('Flip',w,vbl+stimflipnum*ifi);

             
             Screen('FillRect',w,fixcolor,fixrects);
             vbl=Screen('Flip',w,vbl+fixflipnum*ifi);
         end

         if exp_term
             Priority(0);
             break;
         end

         Screen('FillRect',w,fixcolor,fixrects);
         Screen('Flip',w);
         if blockind<numblocks
         vbl=log(blockind+1).onset+fixini+run_starttime;
         end

     end
     
    if exp_term
        Priority(0);
        break;
    end
    % button response check
    [KeyIsDown, firstPress]=PsychHID('KbQueueCheck',devicenum); % Collect keyboard events since KbQueueStart was invoked
            if KeyIsDown
                pressedKey=find(firstPress);
                keyname=KbName(pressedKey);
                presstimetemp=firstPress(pressedKey);
                [pTime,pInd]=sort(presstimetemp,2); % order multiple presses by press time, choose the first pressed button

                presstime=pTime(1)-RTstartTime; % for button press trials only

                    for n=1:size(pressedKey,2) % abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',devicenum);
                            PsychHID('KbQueueRelease',devicenum);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind-1).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
                    log(blockind-1).resp=presstime; % RT, correct for only button press blocks
                    log(blockind-1).resptime=pTime(1)-run_starttime; % resptime is correct for all blocks
                    PsychHID('KbQueueStop',devicenum);                    
                end
            end
   PsychHID('KbQueueStop',devicenum);
   
%    [KeyIsDown2, firstPress2]=PsychHID('KbQueueCheck',devicenumkey); % Collect keyboard events since KbQueueStart was invoked
%             if KeyIsDown2
%                 pressedKey=find(firstPress2);
%                 keyname=KbName(pressedKey);
%                 presstimetemp=firstPress2(pressedKey);
%                 [pTime,pInd]=sort(presstimetemp,2); % order multiple presses by press time, choose the first pressed button
% 
%                 presstime=pTime(1)-RTstartTime; % for button press trials only
% 
%                     for n=1:size(pressedKey,2) % abort exp
%                         if strcmp(KbName(pressedKey(n)),esckey)==1
%                             exp_term=1;
%                             PsychHID('KbQueueStop',devicenumkey);
%                             PsychHID('KbQueueRelease',devicenumkey);
%                             break;
%                         end
%                     end
%                 if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
%                     log(blockind-1).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
%                     log(blockind-1).resp=presstime; % RT, correct for only button press blocks
%                     log(blockind-1).resptime=pTime(1)-run_starttime; % resptime is correct for all blocks
%                     PsychHID('KbQueueStop',devicenumkey);                    
%                 end
%             end
%    PsychHID('KbQueueStop',devicenumkey);
   
   if exp_term
       Priority(0);
       PsychHID('KbQueueStop',devicenum);
       PsychHID('KbQueueRelease',devicenum);
%        PsychHID('KbQueueStop',devicenumkey);
%        PsychHID('KbQueueRelease',devicenumkey);
%        PsychHID('KbQueueStop',devicenumtrigger);
%        PsychHID('KbQueueRelease',devicenumtrigger);
       PsychPortAudio('Close');
       break;
   end

             
end



% fixation (end)
WaitSecs(fixend); % end waiting
run_endtime=GetSecs;
ShowCursor;
Priority(0);
Screen('CloseAll');
PsychPortAudio('Close');
catch exception
    Screen('CloseAll');
    PsychPortAudio('Close');
    rethrow(exception)
end

%% Compute SDT per trial
nHit=0;
nMiss=0;

for ind=1:numblocks
    log(ind).SDT=0;
    if log(ind).cat==3 || log(ind).cat==4
    
%        if log(ind).resp<1.3 & log(ind).resp>0.3
       if log(ind).key
           log(ind).SDT=1;
           nHit=nHit+1;                  
       else
           log(ind).SDT=2;
           nMiss=nMiss+1;
       end
    end
end


result.subjno=subjno;
result.subjname=subjname;
result.log=log;
result.duration=run_endtime-run_starttime;
result.nHit=nHit;
result.nMiss=nMiss;


% save results
resextension='.mat';
resnameappend=[];
resnameappendnum=0;
resnamestring=sprintf('result_%s_%s_PinelLanguage_run%d',subjno,subjname,runnum);
resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
respath=fullfile(dirdata,resultfolder,resname);

if exist(resultfolder,'dir')==0
mkdir(resultfolder);
end
save('subjPinelLanguage.mat','subjno','subjname','distance','screenpx','screenwid');

while exist(respath,'file')
    resnameappendnum=resnameappendnum+1;
    resnameappend=sprintf('_%s',string(resnameappendnum));   
    resnamestring=sprintf('result_%s_%s_PinelLanguage_run%d',subjno,subjname,runnum);
    resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
    respath=fullfile(dirdata,resultfolder,resname);
end
save(respath,'result');   
save(fullfile(dirdata,resultfolder,'subjPinelLanguage.mat'),'subjno','subjname','distance','screenpx','screenwid');
