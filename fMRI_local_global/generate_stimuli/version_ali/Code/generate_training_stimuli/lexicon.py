'''
# =============================================================================
# French lexicon (french local-global) 
# =============================================================================
'''
# Initialize features
numbers=['sing','plur']

# =============================================================================
# INITIALIZE CONTAINERS
# =============================================================================
#~~~~~~
# DETERMINERS, HUMANS AND ADJECTIVES
#~~~~~~
humans, adj, det= [{} for i in range(0,3)]

for number in numbers: 
    humans[number]={}
    adj[number]   ={}
    det[number]   ={}




# =============================================================================
# POPULATE CONTAINERS
# =============================================================================

#~~~~~~~~~
# ADVERBS
#~~~~~~~~~
adv={}
adv['pp']= ['near']
adv['obj']=['that']


#~~~~~~
# HUMANS
#~~~~~~

human_sing=[
        'athlete',
        'baker',
        'doctor',
        'farmer',
        'teacher',
        'lawyer',
        'actor',
      	'author',
     	'banker',
    #        'blogger',
        'barber',
        'chef',
        #'dentist',
        'judge',
        'painter',
        'pilot',
        'plumber',
        'tailor',
        'waiter',
        'vet',
#        'architect',
        'builder'
    ]

human_plur=[
        'athletes',
        'bakers',
        'doctors',
        'farmers',
        'teachers',
        'lawyers',
        'actors',
    	'authors',
     	'bankers',
#        'blogger',
        'barbers',
        'chefs',
        #'dentists',
        'judges',
        'painters',
        'pilots',
        'plumbers',
        'tailors',
        'waiters',
        'vets',
#        'architect',
        'builders'
    ] 


humans['sing']=human_sing
humans['plur']=human_plur



# =============================================================================
# DETERMINERS
# =============================================================================

types=['definite','indefinite','demonstrative']
det={}

for number in ['sing','plur']:
    det[number]={}
    for t in types:
        det[number][t]={}
        
#--------------------------
# DEFINITE
#--------------------------
det['sing']['definite']='the'
det['plur']['definite']='the'
#--------------------------
# INDEFINITE
#--------------------------
det['sing']['indefinite']='a'

#--------------------------
# DEMONSTRATIVE
#--------------------------
det['sing']['demonstrative']='this'
det['plur']['demonstrative']='these'



# =============================================================================
# ACTIVITIES 
# =============================================================================
activities = [
        'climbing',
        # 'skiing',
        'cooking',
        # 'shopping',
        #'painting',
        # 'studying',
        'walking',
        # 'cycling',
        #'farming',
        'fencing',
        'gambling',
        #'knitting',
        #'acting',
        'boxing',
        'bowling',
        'camping',
        'fishing',
        #'jogging',
        #'dancing',
        # 'sailing',
        #'running',
        'hunting',
        # 'swimming',
        'driving']




# =============================================================================
# VERBS
# =============================================================================


verb_intr_sing=[
#        'smiles',
        'cries',
        'laughs',
        'prays',
        'coughs',
#        'sneezes',
#        'sits',
        'runs',
#        'swims',
#        'lies',
        'dies',
#        'studies',
        'arrives',
#        'moves',
        'leaves',
#        'turns'
    ]

verb_intr_plur=[
#        'smile',
        'cry',
        'laugh',
        'pray',
        'cough',
#        'sneeze',
#        'sits',
        'run',
#        'swims',
#        'lies',
        'die',
#        'studies',
        'arrive',
#        'moves',
        'leave',
#        'turns'
    ]


verb_tran_sing=[
        'likes',
        'loves',
        'hates',
        # 'avoids',
        'dislikes',
        'fears',
        #'prefers',
        # 'abhors',
        # 'avoids',
         'detests',
        # 'dreads',
        # 'evades',
        # 'fancies'
    ]

verb_tran_plur=[
        'like',
        'love',
        'hate',
        # 'avoid',
        'dislike',
        'fear',
        'prefer',
        # 'abhor',
        # 'avoid',
         'detest',
        # 'dread',
        # 'evade',
        # 'fancy'
    ]

verbs={}
for tr in ['intr','tran']: verbs[tr]={}    

verbs['intr']['sing']=verb_intr_sing
verbs['intr']['plur']=verb_intr_plur

verbs['tran']['sing']=verb_tran_sing
verbs['tran']['plur']=verb_tran_plur


# =============================================================================
# POPULATE A SUMMARY DICTIONARY
# =============================================================================
words={}
words['verbs']  =verbs
words['humans'] =humans
words['det']    =det
words['adv']    =adv
words['activities']=activities
