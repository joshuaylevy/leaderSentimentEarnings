import sys
import os
import re
import time
import pandas as pd
import numpy as np
from datetime import datetime as dt
from random import randint
from coreference_resolve import main



print("----------IN THE PYTHON SCRIPT NOW----------")
### The Logic behind this file:
# The Allen NLP Predictor object does not permit multiprocessing (https://github.com/allenai/allennlp/issues/2102)
# So, in an effort to get around this, I instead instantiate 10 different machines each with a single core, and each with its own, independent predictor object.
# In order the prevent a conflict of two of these machines trying to do coreference resolution on the same leader, I give every leader and every machine an "index" (0-9) where machine i does coreference resolution on only on leaders that also have index i
# This is not the most efficient way to handle things as there maybe some leaders (IE US Presidents and UK PMs) that have very long lists of articles that cannot be parallelized. However, I'm supposing that those leaders are basically uniformly distributed throughout the indexing process.


# Pull in arguments from the command (i.e. sbatch submit_array.sh contents) that ran this file. 
system_arguments = sys.argv
# Delete the first element of the arguments list (will always be the name of the script'manager.py')
system_arguments.pop(0)

# Instantiate and construct a map of arguments about what subset of all potential leaders we should begin work on. Arguments of interest are as follows: [INDEXER NUM, LOGICAL STATUS, CCODE(s), LEADID(s)]
arguments_map = {}
arguments_map['indexer_num'] = system_arguments[0]

for argument in system_arguments[1:4]:
    key_val_list = argument.split('XXX')
    val_list = key_val_list[1:]
    arguments_map[key_val_list[0]] = val_list
   
print("ARGUMENTS:")
print(arguments_map)

# Sleep some random amount of time between 0 and 1 seconds (in an effort to prevent all jobs from trying to read the same sheet at exactly the same time.)
time.sleep(randint(1,10)/10)

# Check to see if the manager_sheet has been created. (We will eventually use this for submitting large batches of leaders)
if not os.path.isfile('manager_sheet.csv'):
    #Identify all possible leaders
    manager_sheet_df = pd.read_csv('all_leaders_econ_styling.csv')
    manager_sheet_df = manager_sheet_df.drop_duplicates(subset=['leadid'], keep='first')

    manager_sheet_df.reset_index(drop=True, inplace=True)

    #Create an index type for each leader
    manager_sheet_df['row_number'] = manager_sheet_df.index
    manager_sheet_df = manager_sheet_df.assign(index_number=manager_sheet_df.row_number % 10)

    # Note that we haven't started resolution yet (THIS LINE NEEDS TO CHANGE)
    # df['resolved'] = 0
    manager_sheet_df.to_csv('manager_sheet.csv', index=False)
    df = manager_sheet_df[manager_sheet_df.index_number == int(arguments_map.get('indexer_num'))]

else:
    df = pd.read_csv('manager_sheet.csv')
    df = df[df.index_number == int(arguments_map.get('indexer_num'))]

print(df.tail(5))


def resolvedPreExists(name, leadid):
    resolved_path = "leader_resolved/{namestr}_resolved_{leadidstr}_temp.csv".format(namestr=name, leadidstr=leadid)
    if os.path.isfile(resolved_path):
        return True
    else:
        return False

def noteComplete(leadid_param):
    manager_temp_df = pd.read_csv('manager_sheet.csv')
    # manager_temp_df.loc[manager_temp_df['leadid']==leadid_param, 'resolved'] = 1
    manager_temp_df.to_csv('manager_sheet.csv', index=False)

def perLeaderResolve(leader_subset_df):
    for obs in df.index.tolist():
        term_info = df.loc[obs, :]
        print(term_info)
        name = term_info.econ_style_last.replace('.','')
        name = name.replace(' ', '')
        leadid_preserved = term_info.leadid
        leadid_check = term_info.leadid.replace('.','')
        
        if resolvedPreExists(name, leadid_check):
            print("{} (leadid: {}) has already been resolved, proceeding. Check leader_resolved folder".format(name, leadid_preserved))
            noteComplete(leadid_preserved)
            continue
        else:
            num_articles_resolved = main(name, leadid_preserved)
            noteComplete(leadid_preserved)
            print("Newly completed ({} articles had coreferences resolved): {} ({})".format(num_articles_resolved, name, leadid_preserved))

#def checkForLong():

    

# WE ALWAYS TAKE THE MOST LOGICALLY RESTRICTIVE CONDITION:
# MOST RESTRICTIVE: leadid ----------  ccode ---------- logical==all :LEAST RESTRICTIVE
if arguments_map.get('leadid')[0] != '':
    leadid_list = arguments_map.get('leadid')
    print("VALID LEADID ARGUMENT RECEIVED: {}".format(leadid_list))
    print(df.head(1))
    df = df[df.leadid.isin(leadid_list)]
    perLeaderResolve(df)

elif arguments_map.get('ccode')[0] != '':
    ccode_list = arguments_map.get('ccode')
    ccode_list = np.array(ccode_list)
    df = df[df.ccode.isin(ccode_list.astype(int))]
    print("VALID CCODE ARGUMENT RECEIVED: {}".format(ccode_list))
    print(df.head(1))
    perLeaderResolve(df)
    
else:
    print('b')
