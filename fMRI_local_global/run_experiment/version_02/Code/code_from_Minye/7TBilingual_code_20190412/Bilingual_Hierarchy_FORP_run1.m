% Bilingual hierarchy frequency exp at 7T. 
% Version 20190218

% stimuli categories=14;
% Original coding(num sets, 12 stims per set): 
% cat1=q_hf_he; cat2=q_hf_le; cat3=q_lf_he; cat4=q_lf_le; cat5=b_hf_he;
% cat6=b_hf_le; cat7=b_lf_he; cat8=b_lf_le;cat9=l_hf_he; cat10=l_hf_le;
% cat11=l_lf_he; cat12=l_lf_le; cat13=e_words; cat14=f_words;
% cat15=resting block
%
% q/b/l/h/l/f/e=quadrigram/bigram/letter/high frequent/low frequent/French/English;


% central presentation; 
% buttons:
% Press esc to exit. 
% 60 trials per condition (12 trials x 5 blocks) per run; 
% 3 runs in total;
% Button press recording using PsychHID, KbQueueCheck. 
% log by blocks. 
% response time computed upon ###### presentation, logged to the later presented stimulus during response. 
% fixation dot always present
 
% Screen resolution=1920x1080; screen size=69.84 cm; screen distance=195 cm;
% font size=66;
% button boxes keys=b,y; scanner trigger=t;

% Specific to matlab toolboxes: replaced functions in the statistics toolbox 
% with the ones in psychtoolbox: randperm->NRandPerm; randsample->RandSel;


clear;
subjno=input('Please input date (YYYYMMDD):', 's');
subjname=input('Please input subject number:', 's');

% load('subjBilingualHierarchy.mat'); % info: assigned lists, assigned lists with oddball;
runnum=1;


AssertOpenGL;
KbName('UnifyKeyNames');
%% trial timing definition
numblocksstring=70; % 14 categories x 5blocks (per run)
numblocksrest=7; % rest blocks
numblocks=numblocksstring+numblocksrest; % total number of blocks per run

stimdur=0.15; % letter string presentation time
fixdur=0.2; % ITI between letter strings

fixini=16; % initial fixation period
fixend=14; % fixation period at the end of the run

% lettershift=2; % stimuli presentation, number of letters away from the fixation dot (1 or 2)
rendershift=4; % in pixels, specific for text renderer 1. 
stimfont='Consolas';
instructfont='Courier New';

listlength=12; % number of strings per list

distance=195;% temporary
screenwid=69.84; % temporary
screenpx=1920; % temporary
% theta=atan(stimwidth/2/distance)*180/pi*2;

% contents of the instruction screen, modify here. 
textstart='Waiting for the scanner trigger'; % lower line
textinstruct='Please fixate on the fixation dot throughout the experiment'; % upper line

% check FORP key devices and get device indices
clear PsychHID; 
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices;
[logicalTrig,locationTrig]=ismember({'Current Designs, Inc. TRIGI-USB'},productNames);% trigger device
[logicalButt,locationButt]=ismember({'Arduino LLC Arduino Leonardo'},productNames);% 2-button device
[logicalKey,locationKey]=ismember({'Dell Dell USB Keyboard'},productNames);% PC keyboard

devicenumtrigger=allInfos{locationTrig}.index;%temporary
devicenum=allInfos{locationButt}.index;
devicenumkey=allInfos{locationKey}.index;

% define the corresponding keys of the button box here
% use KbName('KeyNames') to check the key correspondence in the current system
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


stimsize=ceil(22/640*screenpx); % font size
%stimsize=66;
stimcolor=[0 0 0];
BGcolor=[128 128 128];
fixcolor=[112 219 96]; % before: [41 130 60]; 
% fixsize=7/640*screenpx;
instructsize=22;
fixwidth=8;

dirdata=pwd;
resultfolder=sprintf('%s_%s',subjno,subjname);


%% load stim list file (cells of strings)
% Randomize during the exp: block order
load('Bilingual_Hierarchy_stimlist.mat');% 210 stim lists, 15(lists)x14(categories)x12(strings)

% Set the rand method
rng('shuffle'); % octave specific, turn off; 

% Block randomization: 
% split into 3 runs, save to subjBilingualHierarchy; pick oddball blocks (2/5);
blocklist=1:210;
runlisttemp=repmat(1:3,1,5);

runlist=zeros(15,14); 
for randrunind=1:14 % put 15 lists of each condition to 3 runs
  runlist(1:15,randrunind)=runlisttemp(NRandPerm(15,15));
end
runlist=runlist(:);

runassign(:,1)=blocklist(runlist==1);
runassign(:,2)=blocklist(runlist==2);
runassign(:,3)=blocklist(runlist==3);

runassign(numblocksstring+1:numblocks,:)=211; % place holder for resting blocks

% pick oddball blocks from the string blocks; pick 2 from 5 lists per condition, 14 times per run; 
% randomize per run;
condrandlist=[0 0 0 1 1];
% oddassign=zeros(numblocksstring,3);

for condrand=1:14
    oddrandlist(5*condrand-4:5*condrand)=condrandlist(NRandPerm(5,5));
end
 oddassign=oddrandlist;
 oddassign(numblocksstring+1:numblocks)=0;


blockorder=NRandPerm(numblocks,numblocks); % randomize the block orders per run
currentrunassign=runassign(:,runnum);


% jitter IBI (3.8 3.8 5.8 7.8 7.8s); only jitter the blocks with strings
jittertemp=repmat([3.8 3.8 5.8 7.8 7.8],1,14);
jitterITI=jittertemp(NRandPerm(numblocksstring,numblocksstring));


% jitter of resting blocks
restingjittertemp=[8 10 10 12 8 10 10 12];
restingjitter=restingjittertemp(NRandPerm(numblocksrest,numblocksrest));

%% add trial info, randomized oddball info to log file
log(numblocks).ind=[];
log(1).cat=[];
log(1).type=[];
log(1).code=[];
log(1).odd=[]; % 1=odd; 0=no odd; 
log(1).oddnum=[];
log(1).jitter=[];
log(1).resp=[];
log(1).resptime=[];
log(1).key=[];
log(1).SDT=[]; % 0.3<resp<1.3: 1=hit; otherwise: 2=miss;
log(1).blockstart=[];
log(1).content=[];


restind=1; % for loading resting block jitter info
jitterind=1;
for blockind=1:numblocks
   tempID=currentrunassign(blockorder(blockind));
   log(blockind).ind=tempID;
   log(blockind).cat=stimlist(tempID).cat;
   log(blockind).type=stimlist(tempID).type;
   log(blockind).code=stimlist(tempID).code;
   log(blockind).odd=oddassign(blockorder(blockind));
   log(blockind).content=stimlist(tempID).content; % pick the ind of the noise
   
   if log(blockind).odd==1
     oddnumpick=RandSel(6:listlength,1);
     log(blockind).oddnum=oddnumpick;
     log(blockind).content{oddnumpick,2}=1;% signals the oddball
   end
   if tempID==211
       log(blockind).content=restingjitter(restind);
       log(blockind).jitter=0;
       restind=restind+1;
   else
       log(blockind).jitter=jitterITI(jitterind);
       jitterind=jitterind+1;
   end
end 

%% display trials
try 
  Priority(MaxPriority(0));
  LoadPsychHID;
  Screen('Preference', 'SkipSyncTests', 0);
  PsychImaging('PrepareConfiguration');
  [w,rect]=PsychImaging('OpenWindow',0,BGcolor); % black BG
  Screen('BlendFunction',w,GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
  Screen('Preference', 'DefaultFontSize', instructsize);
  Screen('Preference', 'DefaultFontStyle',0);
  Screen('Preference', 'TextRenderer',1);
  Screen('Preference','DefaultFontName',stimfont);
  Screen('Preference', 'VisualDebugLevel', 3);
  HideCursor;
% window size
  sxsize=rect(3);
  sysize=rect(4);
  cx=sxsize/2;
  cy=sysize/2;

  ovalrects=[cx-fixwidth/2; cy-fixwidth/2; cx+fixwidth/2; cy+fixwidth/2]; % fixation point
        
  hz=Screen('FrameRate',w);
  ifi=Screen('GetFlipInterval',w,100);
  exp_term=0;
  stimflipnum=stimdur/ifi-0.5;
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
PsychHID('KbQueueCreate',devicenumkey,keysOfInterest);
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
            return;
        end
    end


% fixation (start)

Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);
Screen('Flip',w);

WaitSecs(fixini); % starting fixation 
% WaitSecs(1); % for debugging


PsychHID('KbQueueCreate',devicenum,keysOfInterestResp);    
PsychHID('KbQueueCreate',devicenumkey,keysOfInterestResp);   

% pre-set the text box to save computation time
textstim=stimlist(1).content{1,1};
% Screen('TextFont',w,'FVmonospaced');
Screen('TextFont',w,stimfont);
Screen('TextSize',w,stimsize);
Screen('TextStyle',w,0);
wtstim=RectWidth(Screen('TextBounds',w,textstim));
htstim=RectHeight(Screen('TextBounds',w,textstim));
textoneletter='A';
widthoneletter=RectWidth(Screen('TextBounds',w,textoneletter));

xposition=floor(cx-wtstim/2-rendershift);


% block loop
for blockind=1:numblocks
    if log(blockind).cat==15
       resttime=log(blockind).content;
    else
        stimblock=log(blockind).content;
        if log(blockind).odd==1
            stimblock{log(blockind).oddnum}='######';
        end
    end
    
 PsychHID('KbQueueStart',devicenum);
 PsychHID('KbQueueStart',devicenumkey);
 TstartTime=GetSecs;  

 log(blockind).blockstart=TstartTime-run_starttime;   
 
     if log(blockind).cat==15 % resting block
         Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);
         Screen('Flip',w);
         WaitSecs(resttime);
     else % string block
         for stimind=1:listlength
             textstim=stimblock{stimind};
             
             Screen('TextFont',w,stimfont);            
             Screen('DrawText',w,textstim,xposition,cy-htstim/2,stimcolor);
             Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);

             vbl=Screen('Flip',w);
             log(blockind).content{stimind,3}=GetSecs-run_starttime;
             if stimblock{stimind,2}==1
                 respstart=vbl;
             end

             Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);
             vbl=Screen('Flip',w,vbl+stimflipnum*ifi);

             Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);
             vbl=Screen('Flip',w,vbl+(fixflipnum-1)*ifi);
         end

         if exp_term
             Priority(0);
             break;
         end

         Screen('FillOval',w,fixcolor,ovalrects,fixwidth/2+1);
         Screen('Flip',w);
         WaitSecs(log(blockind).jitter);

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
                if log(blockind).odd==1
                    presstime=pTime(1)-respstart;
                else
                    presstime=pTime(1)-TstartTime; % for no-oddball blocks, also able to record keys (button press as a predictor in fMRI analysis)
                end
                    for n=1:size(pressedKey,2) % abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',devicenum);
                            PsychHID('KbQueueRelease',devicenum);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
                    log(blockind).resp=presstime; % RT
                    log(blockind).resptime=pTime(1)-run_starttime;
                    PsychHID('KbQueueStop',devicenum);                    
                end
            end
   PsychHID('KbQueueStop',devicenum);
   
   [KeyIsDownK2, firstPressK2]=PsychHID('KbQueueCheck',devicenumkey); % Collect keyboard events since KbQueueStart was invoked
            if KeyIsDownK2
                pressedKey=find(firstPressK2);
                keyname=KbName(pressedKey);
                presstimetemp=firstPressK2(pressedKey);
                [pTime,pInd]=sort(presstimetemp,2); % order multiple presses by press time, choose the first pressed button
                if log(blockind).odd==1
                    presstime=pTime(1)-respstart;
                else
                    presstime=pTime(1)-TstartTime; % for no-oddball blocks, also able to record keys (button press as a predictor in fMRI analysis)
                end
                    for n=1:size(pressedKey,2) % abort exp
                        if strcmp(KbName(pressedKey(n)),esckey)==1
                            exp_term=1;
                            PsychHID('KbQueueStop',devicenumkey);
                            PsychHID('KbQueueRelease',devicenumkey);
                            break;
                        end
                    end
                if presstime>0 && pressedKey(pInd(1))==keycodemappingind(1) || pressedKey(pInd(1))==keycodemappingind(2)|| pressedKey(pInd(1))==keycodemappingind(3)|| pressedKey(pInd(1))==keycodemappingind(4)|| pressedKey(pInd(1))==keycodemappingind(5) % used button number instead of button content
                    log(blockind).key=keycodemapping(pressedKey(pInd(1))); % key response, button 1-5. 
                    log(blockind).resp=presstime; % RT
                    log(blockind).resptime=pTime(1)-run_starttime;
                    PsychHID('KbQueueStop',devicenumkey);                    
                end
            end
   PsychHID('KbQueueStop',devicenumkey);
   if exp_term
       Priority(0);
       PsychHID('KbQueueStop',devicenum);
       PsychHID('KbQueueRelease',devicenum);
       PsychHID('KbQueueStop',devicenumkey);
       PsychHID('KbQueueRelease',devicenumkey);
       PsychHID('KbQueueStop',devicenumtrigger);
       PsychHID('KbQueueRelease',devicenumtrigger);
       break;
   end

             
end



% fixation (end)
WaitSecs(fixend); % end waiting
run_endtime=GetSecs;
ShowCursor;
Priority(0);
Screen('CloseAll');

catch exception
    Screen('CloseAll');
    rethrow(exception)
end

%% Compute SDT per trial
nHit=0;
nMiss=0;

for ind=1:numblocks
   if log(ind).odd==1
       if log(ind).resp<1.3 & log(ind).resp>0.3
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


% save results
resextension='.mat';
resnameappend=[];
resnameappendnum=0;
resnamestring=sprintf('result_%s_%s_Bilingual_hierarchy7T_run%d',subjno,subjname,runnum);
resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
respath=fullfile(dirdata,resultfolder,resname);

if exist(resultfolder,'dir')==0
mkdir(resultfolder);
end
save('subjBilingualHierarchy.mat','subjno','subjname','runassign','distance','screenpx','screenwid');

while exist(respath,'file')
    resnameappendnum=resnameappendnum+1;
    resnameappend=sprintf('_%s',string(resnameappendnum));   
    resnamestring=sprintf('result_%s_%s_Bilingual_hierarchy7T_run%d',subjno,subjname,runnum);
    resname=sprintf('%s%s%s',resnamestring,resnameappend,resextension);
    respath=fullfile(dirdata,resultfolder,resname);
end
save(respath,'result');   
save(fullfile(dirdata,resultfolder,'subjBilingualHierarchy.mat'),'subjno','subjname','runassign','distance','screenpx','screenwid');
