#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# =============================================================================
# French lexicon (french local-global) 
# =============================================================================
'''

# =============================================================================
# MODULES AND GLOBALS
# =============================================================================
#modules
import os 
import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")

# alliases
join=os.path.join
make=os.makedirs
exists=os.path.exists
see=os.listdir
read=pd.read_csv


# Path to sources
path2sources=join(os.path.realpath('../..'),'Sources','for_lexicon')

# =============================================================================
# FETCH NOUNS & VERBS FROM SOURCES
# =============================================================================
def fetch_nouns_and_verbs():

    nouns=read(join(path2sources, 
                                 [f for f in see(path2sources) if 'nouns' in f][0]),
                          ).dropna()
    
    v1=read(join(path2sources,[f for f in see(path2sources) if 'v1' in f][0]),).dropna()
    
    v2=read(join(path2sources, 
                                 [f for f in see(path2sources) if 'v2' in f][0]),
                          ).dropna()


    return nouns, v1, v2
# =============================================================================
# ADD ARTICLES
# =============================================================================
def articles():
    articles=pd.DataFrame(index=['défini', 'indéfini', 'démonstratif'],
                          columns=['sing','plur'])
    articles.loc['défini'].sing='le'
    articles.loc['défini'].plur='les'    
    articles.loc['indéfini'].sing='un'
    articles.loc['indéfini'].plur='des'
    articles.loc['démonstratif'].sing='ce'
    articles.loc['démonstratif'].plur='ces'  
    
    return articles

# =============================================================================
# ADD PREPOSITIONS
# =============================================================================
def prepositions():
    pp=[
        'près',
        'loin',
        # 'à côté',
        'proche',
        'auprès',
        # 'devant',
        ]
    obj='que'

    return pp, obj

def wrap_up(nouns, v1, v2, articles, pp, obj):
    lexicon={}
    for e in ['nouns', 'v1','v2' ,'articles','prepositions']:
        lexicon[e]={}
    for e in ['nouns', 'v1','v2' , 'articles',]:
        for n in ['sing','plur']:
            lexicon[e][n]={}

    lexicon['nouns']['sing']=nouns.sing.values.tolist()
    lexicon['v1']['sing']=v1.third_s.values.tolist()
    lexicon['nouns']['plur']=nouns.plur.values.tolist()
    lexicon['v1']['plur']=v1.third_p.values.tolist()
    lexicon['articles']['sing']=articles.sing.values.tolist()
    lexicon['articles']['plur']=articles.plur.values.tolist()
    lexicon['prepositions']['pp'] = {} 
    lexicon['prepositions']['obj']={}
    
    lexicon['prepositions']['pp']=pp    
    lexicon['prepositions']['obj']=obj
    lexicon['v2']['sing']=v2.third_s.values.tolist() 
    lexicon['v2']['plur']=v2.third_p.values.tolist()
    lexicon['v2_goes_with']=v2.goes_with.values.tolist()


    return lexicon

# =============================================================================
# STORE lexicon
# =============================================================================
def store_lexicon(lexicon):
    path2lexicon=join(os.path.realpath('../..'),'Lexicon')
    if not exists(path2lexicon): make(path2lexicon)
    fname=join(path2lexicon, 'french_lexicon.p')    

    # Store data (serialize)
    with open(fname, 'wb') as handle:
        pickle.dump(lexicon, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %%
# =============================================================================
# WRAP EVERYTHING INTO A SINGLE CONTAINER
# =============================================================================
print('', 40*'--', '\n', 'Generating the lexicon.', '\n', 40*'--')
nouns, v1, v2=fetch_nouns_and_verbs()
articles=articles()
pp, obj=prepositions()
lexicon=wrap_up(nouns, v1, v2, articles, pp, obj)
store_lexicon(lexicon)


