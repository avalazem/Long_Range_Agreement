function [stimuli_words, stimuli_datasets, training_words, training_dataset] = load_stimuliLocalGlobal(params)
%%%%%%%%%%%%%%%%%%%%%%%%%
% Load the stimuli
%-----------------------

% Load the blocks
% ---------------

warning off;


if strcmp(params.block_type,'visual')
    curr_filename = fullfile(params.text_filename);
    curr_dataset  = readtable(curr_filename);
    % Update the dataset with information regarding the block type
    curr_dataset.block_type=repmat(params.block_type,size(curr_dataset,1),1);
    
    
    stimuli_datasets = curr_dataset;
    % Cell of cells: cell for each sentence, containing cells for each word
    stimuli_words = cellfun(@(x) regexp(x, ' ', 'split'),curr_dataset.sentence, 'UniformOutput',false);
    for trial = 1:numel(stimuli_words)
        stimuli_words{trial} = ...
            stimuli_words{trial}(~cellfun('isempty',stimuli_words{trial}));
    end
    
    
    % Load the training
    % stimuli.
    % -----------------
    tr_stimuli       = fullfile(params.path2stim,'training_visual','training_visual.csv');
    training_dataset = readtable(tr_stimuli);
    training_words   = cellfun(@(x) regexp(x, ' ', 'split'),...
        training_dataset.sentence, 'UniformOutput',false);
    for tt = 1:numel(training_words) % training trial
        training_words{tt} = ...
            training_words{tt}(~cellfun('isempty',training_words{tt}));
    end
 
    
elseif strcmp(params.block_type,'auditory')
    %%%%%%%%%%%%%%%%%%%%%%%%%
    % Load the WAV segments
    %---------------------
    % Here, we need to load both the .csv and the individual .wav files
    filenames=params.filename_auditory;
    curr_filename = params.text_filename;
    curr_dataset  = readtable(curr_filename);
    % Update the dataset with information regarding the block type
    curr_dataset.block_type=repmat(params.block_type,size(curr_dataset,1),1);
    stimuli_datasets = curr_dataset;
    
    stimuli_wavs={};
    for i=1:numel(filenames)
        wav_filename = filenames{i};
        %      copyfile(wav_filename, fullfile(params.defaultpath, '..', 'Logs', sprintf('%s_%s_%s',params.WAVnames{i},timestamp,subses)))
        temp = audioinfo(wav_filename);
        Fs(i) = temp.SampleRate;
        if Fs(i)~=params.freq
            warning(sprintf('WAV file sample rate not %d Hz', params.freq));
        end
        stimuli_wavs{i}(:,:) = audioread(wav_filename);
    end
    stimuli_words=stimuli_wavs;
    
    
    % Load the training
    % stimuli.
    % -----------------
    path2training_auditory=fullfile(params.path2stim,'training_auditory','wavs');
    filenames=dir(path2training_auditory);
    filenames=filenames(3:end);
    filenames={filenames.name};
    
    
    directories={};
    for i =1:length(filenames)
        directories{i}=fullfile(path2training_auditory,filenames{i});
    end
    filenames=directories;
    
    curr_filename=fullfile(params.path2stim,'training_auditory','auditory_training.csv');
    curr_dataset  = readtable(curr_filename);
    % Update the dataset with information regarding the block type
    curr_dataset.block_type=repmat(params.block_type,size(curr_dataset,1),1);
    training_dataset = curr_dataset;
    
    training_wavs={};
    for i=1:numel(filenames)
        wav_filename = filenames{i};
        temp = audioinfo(wav_filename);
        Fs(i) = temp.SampleRate;
        if Fs(i)~=params.freq
            warning(sprintf('WAV file sample rate not %d Hz', params.freq));
        end
        training_wavs{i}(:,:) = audioread(wav_filename);
    end
    training_words=training_wavs;
    
    
    
    
    
end

