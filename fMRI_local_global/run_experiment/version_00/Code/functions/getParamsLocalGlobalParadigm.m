function [params, events] = getParamsLocalGlobalParadigm(debug_mode)
% ###################################################################
% Set the parameters of the experiment such as Refresh rate and paths.
% ###################################################################

%% ========= GENERAL PARAMETERS ==========================================%
params.method = 'ECoG';
params.r_rate = 60;
% ========================================================================%


if debug_mode
    % When the debugging mode is selected the presentation screen will be 
    % smaller and the subject and session cells have the default parameters
    % shown below.
    params.sub_code = 'TX001';
    params.subject = '00';
    params.block = str2double('01');
    params.block_type='visual';
    % photodiode
    params.photodiode = false;
else
    sub_code = inputdlg({'Enter subject CODE'},...
        'Subject Code',1,{''});
    params.sub_code = sub_code{1};
    
    block = inputdlg({'Enter run number'},...
        'Block Number',1,{''});
    params.block=str2double(block{1});
    
    block_type= inputdlg({'Enter block TYPE'},...
        'Block TYPE',1,{''});
    params.block_type=block_type{1};
    % type can only be visual or auditory
    
    if not(strcmp(params.block_type,'auditory'))
            if not(strcmp(params.block_type,'visual'))
                error('Block type must be "auditory" or "visual"')
            end
    end
    % photodiode
    params.photodiode = false;
end

%% ========= PATHS =======================================================%
root=fullfile(pwd,'..');
params.path2intro_slide = fullfile(root,'Stimuli','instructions_sentences.png');
params.defaultpath      	 = fullfile(root,'runParadigm' ,'Code');
params.path2stim        	 = fullfile(root, 'Stimuli');

% ========================================================================%

if ismac || isunix %comp == 'h'
    params.sio  = '/dev/tty.usbserial';
elseif ispc % strcmp(comp,'l')
    params.sio  = 'COM1';
end

%% =========== STIMULI FILE-NAMES =======================================%%
% !!! Danger zone: Do not modify this section of the code. 
% ========================================================================%
dr = dir(fullfile(params.path2stim,params.block_type,['LocalGlobal' num2str(params.block) '*']));
if strcmp(params.block_type,'visual')
    file_path=dir(fullfile(dr.folder, dr.name));
    index=~[file_path.isdir];
    file_path={file_path.name};
    filename=file_path{index};
    
    params.text_filename = fullfile(dr.folder,dr.name,filename);
elseif strcmp(params.block_type,'auditory')

    file_path=dir(fullfile(dr.folder, dr.name,'wavs'));file_path(1:2)=[];
    UnsortedText={file_path.name};
    R = cell2mat(regexp(UnsortedText ,'(?<Name>\D+)(?<Nums>\d+)','names'));
    tmp = sortrows([{R.Name}' num2cell(cellfun(@(x)str2double(x),{R.Nums}'))]);
    sorted_names = strcat(tmp(:,1) ,cellfun(@(x) num2str(x), tmp(:,2),'unif',0));

    filenames={};
    for f=1:numel(file_path)
        curr_filename=fullfile(dr.folder, dr.name, 'wavs', join([sorted_names{f},'.wav']));
        filenames{f}=curr_filename;
    end
    params.filename_auditory=filenames;
    %either Matlab is lame, or I am too tired:
    csv_name=dir([fullfile(dr.folder, dr.name),'/*.csv']);
    
    params.text_filename = fullfile(dr.folder, dr.name, csv_name.name);

    
end

%% =========== TEXT-PRESENTATION PARAMETERS =============================%%
params.font_size    = 120; % Fontsize for words presented at the screen center
params.font_name    = 'Courier New';
params.font_color   = 'ffffff';
%=========================================================================%

%% =========== TIMING PARAMETERS ========================================%%
params.fixation_duration_visual_block   = 0;    % we remove the fixation on the fMRI paradigm 
params.stimulus_ontime                  = 0.25; % Duration of each word
params.stimulus_offtime                 = 0.25; % Duration of black between words
params.SOA_visual                       = 0.5;
params.ISI_to_response_panel            = 1;
params.panel_ontime                     = 1;  % Duration of panel on the screen
params.max_RT                           = 1;  % Maximum allowance for RT.
%params.feedback_time                    = 0.25;

params.ISI_visual                       = 2; % from end of last trial to beginning of next trial


% AUDIO BLOCK
params.fixation_duration_audio_block = 0;
params.ISI_audio = 1;


% convert the default timings to round multiples of the refresh rate
params = convert_toRR(params);


%% %%%%%%% AUDIO params
params.freq=48000; % Ali changed from 44100;
params.vol=1;
params.audioChannels=2;

params.patientChannel=1;  %audio channel number to patient
params.TTLChannel=2;      %channel number for square wave TTL to show when stimulus is running


% ========================================================================%


%% =========== TRIGGER IDs ==============================================%%
%--------- FIXATION(S) ------------- %
% fixation to first word onset       %
events.StartFixation     = 1;     %
% fixation to Decision screen onset  %
events.StartFix2Decision = 10;       %
events.EndFix2Decision   = 15;       %
% fixation during the feedback period%
events.StartFixFeedback  = 100;     %  
events.EndFixFeedback    = 110;

%=====================================
% VISUAL 
%=====================================

%------------------------------------%
%------ WORD ONSETS-OFFSET --------- %
%------------------------------------%
% FIRST WORD ------------------------%
% ----------------- First word onset %
events.first_word_onset = 40;
% ----------------- First word offset%
events.first_word_ofset = 50;
% LAST WORD -------------------------%
% ----------------- Last word onset -%
events.last_word_onset = 60;
% ----------------- Last word offset-%
events.last_word_ofset = 70;
%------------------------------------%
% WORDS -----------------------------%
events.StartWord  = 80;
events.EndWord    = 90;
%------------------------------------%

%=====================================
% AUDITORY
%=====================================
% FIRST WORD ------------------------%
% ----------------- First word onset %
events.auditory_first_word_onset = 45;
% LAST WORD -------------------------%
% ----------------- Last word offset-%
events.auditory_last_word_ofset = 75;


% PANEL
events.StartPanel       = 30;
events.EndPanel         = 35;

% KEY PRESS(ES)
events.PressKey         = 120;



% MISC
events.event255        = 255;
events.eventreset      = 0;
events.ttlwait         = 0.01;
events.audioOnset      = 0;
events.eventResp       = 145;
%=========================================================================%


