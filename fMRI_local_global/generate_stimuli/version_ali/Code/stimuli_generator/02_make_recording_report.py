#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 20:28:32 2021

@author: czacharo
"""
import os
import pandas as pd

see =os.listdir
join=os.path.join
# Path to stimuli
path2stimuli= join(os.path.realpath('../../Stimuli'))
path2reports=join(os.path.realpath('../../Reports'))
if not os.path.exists(path2reports):
    os.makedirs(path2reports)

print('', 40*'--', '\n', 'Generating the Reports.', '\n', 40*'--')

subjects=see(path2stimuli)
#subjects=list(map(lambda x: x.split('_')[-1], subjects))
# now loop over subjects
for subject in subjects: 
    path2subject=join(path2stimuli,subject)
    # now loop over the soas within subject
    blocks=see(path2subject)
    block_numbers, soas =([] for i in range(0,2))
    for block in blocks:
        block_numbers.append(block.split('_')[1])
        soas.append(block.split('_')[-1].split('.')[0])
    q_list=[block_numbers, soas] 
    report= pd.DataFrame.from_records(q_list).T
    report.columns=['BLOCK','SOA']
    report.sort_values('BLOCK', inplace=True)
    report['start']=''    
    report['end']=''    
    report['saved']=''
    report['subject']=subject
    report['nip']=''    
    report['date']=''    
    report['notes']=''    

    
    fname=join(path2reports, subject+'.csv')    
    report.to_csv(fname)