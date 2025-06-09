function present_feedback_slide(params, handles)

available_images=dir(params.path2feedback_slide);

figure_1=fullfile(params.path2feedback_slide,available_images(3).name);
figure_2=fullfile(params.path2feedback_slide,available_images(4).name);
figure_3=fullfile(params.path2feedback_slide,available_images(5).name);
figure_4=fullfile(params.path2feedback_slide,available_images(6).name);

figures={figure_1, figure_2, figure_3, figure_4}; 
randomIndex = randi(size(figures, 2));


% %%%%%% SHOW INTRO SLIDE
intro_img_read = imread(figures{randomIndex});
intro_img = Screen('MakeTexture', handles.win, intro_img_read, [], [], [], [], 1);
Screen('DrawTexture', handles.win, intro_img, [], [], 0);
Screen('Flip',handles.win);
