% Bilingual (EnFr) category localizer (at 7T). Version 20190411
% zhanminye@gmail.com

% Central presentation; 
% Press ESCAPE to exit. 
% Button press recording using PsychHID, KbQueueCheck. 
% Log by blocks. 
% Task: detect a star, appearing in half of the blocks
% per object condition (including checkerboard)
% Response time: for blocks having a star, RT is computed upon star
% presentation. 
% Fixation dot always present. 

% The part that need to be manually defined by the user: See line 39. 
% Screen resolution=? temporarily use 1920x1080; screen size=?; screen distance?;
% button boxes keys? scanner trigger? Number of repetitions? 

% Specific to matlab toolboxes: replaced functions in the statistics toolbox 
% with the ones in psychtoolbox: randperm->NRandPerm; randsample->URandSel;

clear;

%% Parameters for psychtoolbox
KbName('UnifyKeyNames');
% pkg load statistics; %Octave specific: uncomment for octave
AssertOpenGL;
skipscreencheck=0; % skip psychtoolbox screen test 1 or not 0
mainscreen=0;
debug=0;
debugrect=[];
if debug
    debugrect=[100 100 900 700];  
end

%% Collect subject info
subjno=input('Please input date (YYYY/MM/DD):', 's');
subjname=input('Please input subject name:', 's');
inputrunnum=input('Please input the run number:','s');
runnum=str2double(inputrunnum); % the current run number
dirdata=pwd;
resultfolder=sprintf('%s_%s',subjno,subjname);


%% Values specific to the scanner environment.
% define screen size
distance=195;% in cm. temporary
screenwid=69.84; % in cm. temporary
screenpx=1920; % in px. temporary

%% Parameters of the stimulation protocol
% runnum=1; % number of runs
nconditions=9; % number of conditions
catcodes={'Face';'Body';'WordE';'WordF';'Number';'FalseFont';'House';'Tool';'Checker'};
checker_cat_num=9; % checkers are the nth condition (necessary to control flipping of checkers)
nrepetition=5; % number of repetitions (=nb of miniblocks) per condition
n_stim_in_block=20; % number of stimuli in each block
first_pos_oddball=6; % this stimulus is the first which may be replaced with an oddball
nblocks=nconditions*nrepetition;
% the ranks of the 2 checker files in the list of stimuli (i.e. in the mat file)
num_ch1=161;
num_ch2=162;
num_blank=163;
num_oddball=164;

oddballinchecker=0; % whether or not having oddballs also in the checker condition

%% contents of the instruction screen, modify here. 
textstart='Waiting for the scanner trigger'; % lower line
textinstruct='Please fixate on the fixation dot throughout the experiment'; % upper line

%% define the corresponding keys of the button box here
% use KbName('KeyNames') to check the key correspondence in the current system

% check FORP key devices and get device indices
clear PsychHID; 
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices;
[logicalTrig,locationTrig]=ismember({'Current Designs, Inc. TRIGI-USB'},productNames);% trigger device
[logicalButt,locationButt]=ismember({'Arduino LLC Arduino Leonardo'},productNames);% 2-button device
[logicalKey,locationKey]=ismember({'Dell Dell USB Keyboard'},productNames);% PC keyboard


% % devicenum=-1;% default
devicenumtrigger=allInfos{locationTrig}.index;%temporary
devicenumresp=allInfos{locationButt}.index;
devicenumkey=allInfos{locationKey}.index;
% devicenumtrigger=-1;%temporary
% devicenumkey=-1;
% devicenumresp=-1;

% -1: all keyboards; -2: all keypads; -3: all keyboards and keypads
% devicenumtrigger=0;%temporary
% devicenum=0;
trigger='t'; % scanner trigger key value
esckey='ESCAPE'; % escape key
spacekey='space'; % space key
button1='b'; % MR response buttons
button2='y';
button3='g';
button4='r';
button5=',<';

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


%% Stimuli size definition
stimsize=22/640*screenpx; % font size, not used in the script (used pictures instead)
stimcolor=[128 128 128]; % font color
instructsize=22; % instruction font size
fixwidth=8; % width of the fixation point
fixcolor=[112 219 96]; % old: [26 167 19]; % fixation color

% theta=atan(stimwidth/2/distance)*180/pi*2; % for calculating visual
% angles. stimwidth is in cm. theta is in degrees (not radius). 

%% Temporal parameters
fixationstart=6; % fixation at the start of the run. set to 1 or 0 when debugging
fixationend=6; % fixation after the last ITI
jitter_values=[4 6 8]; % durations in seconds between miniblocks, mean set to 6 (see line 142-246)
fix_duration=0.2; % in seconds
stim_duration=0.1;
minresp=0.3; % min RT considered valid
maxresp=1.3; % max RT considered valid

approx_duration= fixationstart + fixationend + nconditions * nrepetition * (n_stim_in_block * (fix_duration + stim_duration) + mean(jitter_values));
% this computes the length per run. 

%% load stimuli file
load('stimlocBilingual_F.mat');% 144 stim pictures, 20(stimuli)*7(categories)+2(checkers)+1(blank)+1(star)

% Set the rand method
% rdsetting=rng('shuffle');
rng('shuffle'); % triggeroctave specific: comment this; 

%% Block randomization: 
blocklist=repmat(1:nconditions,nrepetition,1);
blocklist=blocklist(:);

% Pick oddball blocks; pick half of the repetitions per condition (in the case of odd repetition number: half-1); 
condrandlist=cat(1,ones(floor(nrepetition/2),1),zeros(nrepetition-floor(nrepetition/2),1));
oddassign=[];

for condind=1:nconditions 
    condtemp=condrandlist(NRandPerm(nrepetition,nrepetition));
    oddassign=cat(2,oddassign,condtemp);
end
if oddballinchecker==0 % oddball not in checker condition
    oddassign(:,checker_cat_num)=zeros(nrepetition,1);
end

% currentoddassign=cat(2,ones(1,7*nrepetition),zeros(1,repetition)); % for debugging target presentation;
currentoddassign=oddassign(:); 

% Randomize the block orders; currentoddassign linked to the original blocklist; 
blockorder=NRandPerm(nblocks,nblocks); 

% Jitter IBI (4 6 8s, average=6s); 
if mod(nblocks,3)==2 
   jittertemp=cat(2,repmat(jitter_values,1,floor(nblocks/3)),jitter_values([1 3])); 
else
   jittertemp=cat(2,repmat(jitter_values,1,floor(nblocks/3)),ones(1,mod(nblocks,3))*jitter_values(2));
end
% Randomize jitter
jitterITI=jittertemp(NRandPerm(nblocks,nblocks));

%% Add trial info to the log file
% definition of log fields 
log(nblocks).category=[]; % categories, value: 1-8
log(1).catcontent=[]; % categories in text, see catcodes below. 
log(1).odd=[]; % 1=oddball (star); 0=no oddball; 
log(1).oddnum=[]; % n-th stimulus replaced by the star
log(1).resp=[]; % first button press RT from the star stimulus onset; for no-oddball blocks: RT from block onset;
log(1).resptime=[]; % button press time from the first scanner trigger
log(1).key=[]; % pressed button by the participant
log(1).SDT=[]; % 0.3<resp<1.3: 1=hit; otherwise: 2=miss;
log(1).blockstart=[]; % block onset time, time lapsed from the first scanner trigger

for blockind=1:nblocks
   tempID=blockorder(blockind);
   categoryind=blocklist(tempID);
   log(blockind).category=categoryind;
   log(blockind).catcontent=catcodes{categoryind};
   log(blockind).odd=currentoddassign(tempID);
   if categoryind==checker_cat_num
       log(blockind).content(:,1)=repmat([num_ch1 num_ch2],1,n_stim_in_block/2)'; % switching between the two checkerboards
   else
   contentindtemp=n_stim_in_block*(categoryind-1)+1:n_stim_in_block*(categoryind); 
   log(blockind).content(:,1)=contentindtemp(NRandPerm(n_stim_in_block,n_stim_in_block))'; % randomize n_stim_in_block stimuli within a block
   end
   log(blockind).content(:,2)=0; % flag of oddball stimulus within a block
   
   if log(blockind).odd==1
     oddnumpick=URandSel(first_pos_oddball:n_stim_in_block,1); % pick one stimulus as the oddball
     log(blockind).oddnum=oddnumpick;
     log(blockind).content(oddnumpick,1)=num_oddball;% oddball content: index of the star
     log(blockind).content(oddnumpick,2)=1; % flag of the odd; 
   end
end


%% display trials
try 
  Priority(MaxPriority(mainscreen));
  LoadPsychHID;  
  Screen('Preference', 'SkipSyncTests', skipscreencheck); % set to 1 only when debugging
  PsychImaging('PrepareConfiguration');
  [w,rect]=PsychImaging('OpenWindow',mainscreen,[0 0 0],debugrect); % black BG
  Screen('BlendFunction',w,GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
  Screen('Preference', 'DefaultFontSize', instructsize);
  Screen('Preference', 'DefaultFontStyle',1);
  Screen('Preference', 'TextRenderer',1);
  Screen('Preference', 'DefaultFontName','Courier New');
  Screen('Preference', 'VisualDebugLevel',3); % skip the psychtoolbox welcome screen
  HideCursor;
  sxsize=rect(3); % window size
  sysize=rect(4);
  cx=sxsize/2; % center of screen
  cy=sysize/2;

  ovalrects=[cx-fixwidth/2; cy-fixwidth/2; cx+fixwidth/2; cy+fixwidth/2]; % fixation point (circle)
 
  hz=Screen('FrameRate',w); % stimuli are presented by numbers of frames
  ifi=Screen('GetFlipInterval',w,100);
  stimflipnum=stim_duration/ifi-0.5;
  fixflipnum=fix_duration/ifi-0.5;
  
  exp_term=0; % flag for exiting

  % Instruction screen
  Screen('TextSize',w,instructsize);
  Screen('TextStyle',w,1);
  Screen('TextFont',w,'Courier New');
  wtinstruct=RectWidth(Screen('TextBounds',w,textinstruct));
  htinstruct=RectHeight(Screen('TextBounds',w,textinstruct));
  wtstart=RectWidth(Screen('TextBounds',w,textstart));
  htstart=RectHeight(Screen('TextBounds',w,textstart));
  Screen('DrawText',w,textinstruct,cx-ceil(wtinstruct/2),cy-ceil(htinstruct/2)-30,[255 255 255])
  Screen('DrawText',w,textstart,cx-ceil(wtstart/2),cy-ceil(htstart/2)+30,[255 255 255])
    
  Screen('Flip',w);  
  
  
  
keysOfInterest=zeros(1,256);
keysOfInterest(KbName({spacekey,esckey,trigger}))=1; % initialize keys for the trigger
PsychHID('KbQueueCreate',devicenumtrigger,keysOfInterest);
PsychHID('KbQueueCreate',devicenumkey,keysOfInterest);

PsychHID('KbQueueStart',devicenumtrigger);
PsychHID('KbQueueStart',devicenumkey);
% Get the trigger from the scanner
TTL=0; % flag of starting the experiment
    while TTL==0
        [KeyIsDown, firstPress]=PsychHID('KbQueueCheck',devicenumtrigger); % Wait for FORP TTL (from scanner)
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
        
        [KeyIsDownK, firstPressK]=PsychHID('KbQueueCheck',devicenumkey); % Wait for key presses from keyboard (for exiting)
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
            return;
        end
    end


% Fixation (start)
% Pre-set the text and picture box to save computation time
stimpicsize=size(stimloc(1).img);
wstim=stimpicsize(1)/2;
hstim=stimpicsize(1)/2;
pictblk=Screen('MakeTexture',w,stimloc(num_blank).img); % blank
pictstar=Screen('MakeTexture',w,stimloc(num_oddball).img); % star
Screen('DrawTexture',w,pictblk,[],[cx-wstim,cy-hstim,cx+wstim,cy+hstim]);
Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+2);

Screen('Flip',w);

WaitSecs(fixationstart); % starting fixation 

% Block loop 
PsychHID('KbQueueCreate',devicenumresp,keysOfInterestResp); % initialize response buttons 
PsychHID('KbQueueCreate',devicenumkey,keysOfInterestResp); % also allows inputs from the keyboard

for blockind=1:nblocks
    stimblock=log(blockind).content;
    
 PsychHID('KbQueueStart',devicenumresp)
 PsychHID('KbQueueStart',devicenumkey)
 TstartTime=GetSecs;

 log(blockind).blockstart=TstartTime-run_starttime;    
    for stimind=1:n_stim_in_block
        stimpic=Screen('MakeTexture',w,stimloc(stimblock(stimind,1)).img);
        Screen('DrawTexture',w,stimpic,[],[cx-wstim,cy-hstim,cx+wstim,cy+hstim]); % stimulus
        Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+2); % fixation

        
        vbl=Screen('Flip',w);
        log(blockind).content(stimind,3)=GetSecs-run_starttime;
        if stimblock(stimind,2)==1 % flag of oddball
           respstart=vbl;
        end
        
        Screen('DrawTexture',w,pictblk,[],[cx-wstim,cy-hstim,cx+wstim,cy+hstim]);
        Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+2);      
        vbl=Screen('Flip',w,vbl+stimflipnum*ifi);
        
        Screen('DrawTexture',w,pictblk,[],[cx-wstim,cy-hstim,cx+wstim,cy+hstim]);
        Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+2);
        vbl=Screen('Flip',w,vbl+(fixflipnum-1)*ifi);
        Screen('Close',stimpic); % Closed each stimulus texture to prevent memory overflow. Otherwise they accumulate in the memory. 
    end
        
    if exp_term
        Priority(0);
        break;
    end
    
    Screen('DrawTexture',w,pictblk,[],[cx-wstim,cy-hstim,cx+wstim,cy+hstim]);
    Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+2);
    Screen('Flip',w);
    WaitSecs(jitterITI(blockind));
    
    % Button response check and logging at the end of the block (including the inter-block interval, in case of late button presses)
    [KeyIsDown, firstPress]=PsychHID('KbQueueCheck',devicenumresp); % Collect keyboard events since KbQueueStart was invoked at the beginning of the block
            if KeyIsDown
                pressedKey=find(firstPress);
                keyname=KbName(pressedKey);
                presstimetemp=firstPress(pressedKey);
                [pTime,pInd]=sort(presstimetemp,2); % Order multiple presses by press time, choose the first pressed button
                if log(blockind).odd==1
                    presstime=pTime(1)-respstart;
                else
                    presstime=pTime(1)-TstartTime; % for no-oddball blocks, also able to record keys (button press as a predictor in fMRI analysis)
                end
                    for n=1:size(pressedKey,2) % Abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',devicenumresp);
                            PsychHID('KbQueueRelease',devicenumresp);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1)|| pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. Will only log these button presses
                    log(blockind).resp=presstime; % RT
                    log(blockind).resptime=pTime(1)-run_starttime;
                    PsychHID('KbQueueStop',devicenumresp);
                end
            end         
   PsychHID('KbQueueStop',devicenumresp);
   
   [KeyIsDownK2, firstPressK2]=PsychHID('KbQueueCheck',devicenumkey); % Collect keyboard events since KbQueueStart was invoked at the beginning of the block
               if KeyIsDownK2
                   pressedKey=find(firstPressK2);
                   keyname=KbName(pressedKey);
                   presstimetemp=firstPressK2(pressedKey);
                   [pTime,pInd]=sort(presstimetemp,2); % Order multiple presses by press time, choose the first pressed button
                   if log(blockind).odd==1
                       presstime=pTime(1)-respstart;
                   else
                       presstime=pTime(1)-TstartTime; % for no-oddball blocks, also able to record keys (button press as a predictor in fMRI analysis)
                   end
                   for n=1:size(pressedKey,2) % Abort exp
                       if strcmp(KbName(pressedKey(n)),esckey)==1
                           exp_term=1;
                           PsychHID('KbQueueStop',devicenumkey);
                           PsychHID('KbQueueRelease',devicenumkey);
                           break;
                       end
                   end
                   if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1)|| pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                       log(blockind).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. Will only log these button presses
                       log(blockind).resp=presstime; % RT
                       log(blockind).resptime=pTime(1)-run_starttime;
                       PsychHID('KbQueueStop',devicenumkey);
                   end
               end
   PsychHID('KbQueueStop',devicenumkey);
   if exp_term
       Priority(0);
       PsychHID('KbQueueStop',devicenumresp);
       PsychHID('KbQueueRelease',devicenumresp);
       PsychHID('KbQueueStop',devicenumkey);
       PsychHID('KbQueueRelease',devicenumkey);
       PsychHID('KbQueueStop',devicenumtrigger);
       PsychHID('KbQueueRelease',devicenumtrigger);
       break;
   end

             
end



% Fixation (end of experiment)
WaitSecs(fixationend); 
run_endtime=GetSecs;
ShowCursor;
Priority(0);
PsychHID('KbQueueStop',devicenumresp);
PsychHID('KbQueueRelease',devicenumresp);
PsychHID('KbQueueStop',devicenumkey);
PsychHID('KbQueueRelease',devicenumkey);
PsychHID('KbQueueStop',devicenumtrigger);
PsychHID('KbQueueRelease',devicenumtrigger);
Screen('CloseAll');


catch exception
%     PsychHID('KbQueueStop',devicenumresp);
%     PsychHID('KbQueueRelease',devicenumresp);
%     PsychHID('KbQueueStop',devicenumkey);
%     PsychHID('KbQueueRelease',devicenumkey);
    Screen('CloseAll');
    rethrow(exception)
end


%% Compute hit/miss per trial (logged in the field SDT)
nHit=0;
nMiss=0;

for ind=1:nblocks
   if log(ind).odd==1
       if log(ind).resp<maxresp & log(ind).resp>minresp
           log(ind).SDT=1;
           nHit=nHit+1;                  
       else
           log(ind).SDT=2;
           nMiss=nMiss+1;
       end
   else
       log(ind).SDT=0;
   end    
end


result.subjno=subjno;
result.subjname=subjname;
result.log=log;
result.duration=run_endtime-run_starttime;
result.nHit=nHit;
result.nMiss=nMiss;

resextension='.mat';
resnameappend=[];
resnameappendnum=0;
resnamestring=sprintf('result_%s_%s_categoryloc7T_F_run%d',subjno,subjname,runnum);
resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
respath=fullfile(dirdata,resultfolder,resname);

if exist(resultfolder,'dir')==0
mkdir(resultfolder);
end
save('subjCatLocalizer.mat','subjno','subjname','currentoddassign','distance','screenpx','screenwid');

while exist(respath,'file')
    resnameappendnum=resnameappendnum+1;
    resnameappend=sprintf('_%s',string(resnameappendnum));   
    resnamestring=sprintf('result_%s_%s_categoryloc7T_F_run%d',subjno,subjname,runnum);
    resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
    respath=fullfile(dirdata,resultfolder,resname);
end
save(respath,'result');   

save(fullfile(dirdata,resultfolder,'subjCatLocalizer.mat'),'subjno','subjname','currentoddassign','distance','screenpx','screenwid');
