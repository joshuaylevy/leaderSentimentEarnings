import pandas as pd
import numpy as np
import multiprocessing as mp
from allennlp.predictors.predictor import Predictor
from datetime import datetime as dt
from dateutil.relativedelta import *
from tqdm import tqdm
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from functools import partial
import os
import allennlp_models.tagging
import spacy
import re
import time


# os.environ["TOKENIZERS_PARALLELISM"] = "true"
chunksize = 1000
date_format = '%d-%b-%y'

custom_date_parser = lambda x: dt.strptime(x, date_format)

## DETERMINING IF WE NEED TO CREATE A DATE-INDEX
## PREAMBLE FUNCTIONS 
def checkDateIndex():

    date_index_reference = 'issue_sheet_index.csv'
    # chunksize = 1000
    date_format = '%d-%b-%y'
    custom_date_parser = lambda x: dt.strptime(x, date_format)

    formatted_csv_path = 'formatted_csvs/'
    formatted_csv_stub = 'formatted_sub_article_text'
    suffix = '.csv'

    if not os.path.isfile(date_index_reference):
        print('date index needs to be instantiated, proceeding to do that')
        #Initialize the index df
        index_df = pd.DataFrame([], columns=['date_issue', 'sheet_path', 'sheet_num'])    

        # GOING THROUGH EACH FORMATTED CSV
        for sub_csv_index in tqdm(range(0,124)):
            read_path = formatted_csv_path + formatted_csv_stub + str(sub_csv_index) + suffix
            temp_df =  pd.read_csv(read_path, parse_dates=['date'], date_parser=custom_date_parser)

            # Identifying unique dates
            temp_df = temp_df.drop_duplicates(subset=['date'], keep='first')
            temp_df = temp_df['date']

            temp_index = pd.DataFrame([], columns=['date_issue', 'sheet_path', 'sheet_num'])

            # Pulling out the info of interest 
            for issue_row in temp_df.index.tolist():
                row_obs = temp_df.loc[issue_row]
                # recall that temp_df is now just a single column of 'date
                temp_index.loc[issue_row, 'date_issue'] = temp_df.loc[issue_row].date()
                temp_index.loc[issue_row, 'sheet_path'] = formatted_csv_path + formatted_csv_stub + str(sub_csv_index) + suffix
                temp_index.loc[issue_row, 'sheet_num'] = sub_csv_index
            ### REMEMBER THAT A DATE MIGHT APPEAR IN/CROSS OVER MORE THAN ONE SHEET
            # Need to concat and reset indices because first instances of different issues may appear on the same row (i.e. "index" of temp_df) of different sheets. Need to do this to avoid conflicts
            index_df = pd.concat([index_df, temp_index], ignore_index=True)
            index_df.reset_index(drop=True, inplace=True)
            index_df['date_issue'] = pd.to_datetime(index_df['date_issue'])

        index_df.to_csv(date_index_reference, index=False)
            
    else:
        print('Issues are already indexed for their dates, carry on')
        index_df = pd.read_csv(date_index_reference)
        index_df['date_issue'] = pd.to_datetime(index_df['date_issue'])

    # print(index_df.head(5))

    return index_df
        
def leaderWindowConstructor(index_df):

        ### READING IN LEADER TERM DATA
    leader_term_name_df = pd.read_csv('all_leaders_econ_styling.csv', encoding='latin1')
    leader_term_name_df = leader_term_name_df.drop_duplicates(subset='leadid')


    leader_term_name_df['term_start'] = dt.now
    leader_term_name_df['term_end'] =dt.now

    # leader_term_name_df
    for index in tqdm(leader_term_name_df.index.tolist()):
        # FORMAT: start = dt(year, month, day)
        leader_term_name_df.loc[index, 'term_start'] = dt(leader_term_name_df.loc[index, 'start_year'], leader_term_name_df.loc[index, 'start_month'], leader_term_name_df.loc[index, 'start_date'])
        
        # Push to the end of the month as far as possible (accounting for leap years)
        # Note that we are pushing the end of the term out 6 months anyway (in case we miss an issue printed on the 29th-31st)
        leader_term_name_df.loc[index, 'term_end'] = dt(leader_term_name_df.loc[index, 'end_year'], leader_term_name_df.loc[index, 'end_month'], 28)

    # print(leader_term_name_df.head(5))


    # MATCHING TERM-WINDOWS (term length +/- 6 months) WITH ECONOMIST ISSUE DATES
    # We then pair this with the dat_index_reference.csv to figure out which chunks of formatted_compiled_articles.csv we should read
    six_month_margin = relativedelta(months = 6)

    leaders_windows_indices_df = leader_term_name_df

    # Constructing the 6 month window around the term start
    leaders_windows_indices_df = leaders_windows_indices_df.assign(leader_aprox_starts = lambda df: df.term_start - six_month_margin)
    leaders_windows_indices_df = leaders_windows_indices_df.assign(leader_aprox_ends = lambda df: df.term_end + six_month_margin)
    leaders_windows_indices_df['leader_aprox_starts'] = pd.to_datetime(leaders_windows_indices_df['leader_aprox_starts'])

    # Merge window-start and window-end dates with the "nearest" (FORWARD OR BACKWARD) Economist issue date.
    # Read in that issue's starting row/index
    # PRE-TERM
    leaders_windows_indices_df = leaders_windows_indices_df.sort_values(by=['leader_aprox_starts'])
    leaders_windows_indices_df = pd.merge_asof(left=leaders_windows_indices_df, right=index_df, left_on='leader_aprox_starts', right_on='date_issue', direction='nearest')
    leaders_windows_indices_df = leaders_windows_indices_df.rename(columns={'date_issue' : 'date_start_issue', 'sheet_path' : 'start_sheet_path', 'sheet_num' : 'start_sheet_num'})

    # POST-TERM
    leaders_windows_indices_df = leaders_windows_indices_df.sort_values(by=['leader_aprox_ends'])
    leaders_windows_indices_df = pd.merge_asof(left=leaders_windows_indices_df, right=index_df, left_on='leader_aprox_ends', right_on='date_issue', direction='nearest')
    leaders_windows_indices_df = leaders_windows_indices_df.rename(columns={'date_issue': 'date_end_issue', 'sheet_path': 'end_sheet_path', 'sheet_num' : 'end_sheet_num'})

    # Add in titles and adjectives
    adjectives_df = pd.read_csv('national_titles_adjectives.csv').drop(columns=['country'])
    leaders_windows_indices_df = pd.merge(leaders_windows_indices_df, adjectives_df, how='left', on='ccode')


    print(len(leader_term_name_df))

    return leaders_windows_indices_df


# COREFERENCE RESOLUTION HELPER FUNCTIONS
# IN ONE WAY OR ANOTHER THESE ALL  HELP identifyMainCluster
def fuzzy_leader_search(plain_text, choices): 
    honorifics = ["Mr", "Ms", "Miss", "Mrs"]
    topSetMatch = process.extract(plain_text, choices, scorer=fuzz.token_set_ratio)

    for alias in topSetMatch:
        # IF WE ARE CONSIDERING Mr/Ms _____ AS THE CANDIDATE HONORIFIC RAISE THE THRESHOLD FOR MATCH TO 100 (BASICALLY PERFECT MATCH)
        if alias[0].split()[0] in honorifics:
            if alias[1] == 100:
                return True
            else:
                continue
        # WE ARE CONSIDERING A FULL NAME OR A TILE NAME Like President ____
        else:
            if alias[1] >= 90:
                return True

    return False 

def leaderAliasGenerator(leader_observation):
    ## SOME DOCUMENTATION
    # https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
    # https://github.com/seatgeek/fuzzywuzzy
    
    
    row = leader_observation
    full_name_tuple = (row.econ_style_first, row.econ_style_last)
    full_name = str.title(' '.join(full_name_tuple))

    title_last_pref_tuple = (row.hos_title, row.econ_style_last)
    title_last_pref = str.title(' '.join(title_last_pref_tuple))
    
    # Adding gendered honorifics
    if row.gender == 1:
        hon_list = []
        hon = "Mr"
        hon_last = str.title(' '.join([hon, row.econ_style_last]))
        hon_list.append(hon_last)
    else:
        hon_1 = "Ms"
        hon_last_1 = str.title(' '.join([hon_1, row.econ_style_last]))
        hon_2 = "Miss"
        hon_last_2 = str.title(' '.join([hon_2, row.econ_style_last]))
        hon_3 = "Mrs"
        hon_last_3 = str.title(' '.join([hon_3, row.econ_style_last]))


    choices = [full_name, title_last_pref] + hon_list

    #Adding other/type of honorific if necessary/available
    if type(row.hos_title_other) != float:
        title_last_alt_tuple = (row.hos_title_other, row.econ_style_last)
        title_last_alt = str.title(' '.join(title_last_alt_tuple))
        
        choices.insert(2, title_last_alt)

    # Adding Economist-style alias if necessary/available
    if type(row.econ_style_alias) != float:
        alias = row.econ_style_alias
        econ_alias = str.title(alias)

        choices.insert(2, econ_alias)

    return choices

def identifyMainCluster(clusters, name_vect, document):
    clusters = clusters
    aliases = name_vect

    for cluster in clusters:
        for index_pair in cluster:
            start_index = index_pair[0]
            stop_index = index_pair[1]+1
            cluster_as_string = ' '.join(document[start_index:stop_index])

            top_set_match = process.extract(cluster_as_string, aliases)
            fuzz_match_results = zip(*top_set_match)
            fuzz_match_res_unzipped = list(fuzz_match_results)
            scores = fuzz_match_res_unzipped[1]

            if max(scores) >= 90:
                cluster_index = clusters.index(cluster)
                # print("CLUSTER AS STRING: " + cluster_as_string)
                # print("FUZZY MATCH SCORES: " + str(top_set_match))
                # print("CLUSTER: " + str(cluster))
                # print("INDEX OF THAT CLUSTER" + str(cluster_index))
                return cluster_index

    # There may be instances in which the leader is mentioned but not in a fashion that is sufficiently important to be picked up as an entity by the model. These are usually in instances where the leader is only an object in the sentence and never becomes a subject. In those instances no replacement takes place.

def replaceCoref(name, clusters, cluster_interest_index, document, tokenized_df):
    name_string = name[0]
    print(name_string)
    
    # name = name.split()
    name_pos = name_string + "\'s"
    name_pos = name_pos.split()
    
    # print(cluster_interest_index)
    base_cluster = clusters[cluster_interest_index]
    # print(base_cluster)
    
    #Coreferences are replaced in reverse order so that we as we replace references that occur towards the end of the article we don't have to worry about how new string/list length is affected. That is, the indices identified in base_cluster are still valid.
    rev_cluster  = sorted(base_cluster, key = lambda x: x[0], reverse = True)
    new_doc_list = document

    df = tokenized_df
    # print("REPLACING WITH: " + str(name) + " (or possessive)")
    for index_pair in rev_cluster:
        start_index = index_pair[0]
        stop_index = index_pair[1]+1
        # print("REPLACING: " + str(new_doc_list[start_index:stop_index]))

        # Replacing one element (i.e. pronouns/possessives)
        if start_index == stop_index:
            if containsPossessive(df, start_index, stop_index) == True:
                new_doc_list[start_index:stop_index] = name_pos
            else:
                new_doc_list[start_index:stop_index] = name
            new_doc_list.pop(start_index+2)
        # Replacing two or more elements
        else:
            if containsPossessive(df, start_index, stop_index) == True:
                new_doc_list[start_index:stop_index] = name_pos
            else:
                new_doc_list[start_index:stop_index] = name

    # print(new_doc_list)
    return new_doc_list

def containsPossessive(df, start_index, stop_index):
    possessive_tags = ['POS', 'PRP$']
    cluster_tags = df['tag'].iloc[start_index:stop_index]
    # .isdisjoint returns true if the two sets are disjoin (i.e. do not have any elements interesecting (i.e. does not contain a POS or PRP$)). So negate to return True if "NOT DISJOINT" (CONTAINS POS/PRP$)
    if not set(possessive_tags).isdisjoint(set(cluster_tags)):
        return True
    else:
        return False


# PRIMARY FUNCTION
def termLimitChecker(date, start, end):

    if start <= date <= end: 
        return "IN TERM"
    elif date < start:
        return "PRE TERM"
    else:
        return "POST TERM"

# def resolverFunc(term_info, aliases, predictor, spacy_nlp_obj, chunked_df):
def resolverFunc(term_info, aliases, spacy_nlp_obj, chunked_df):
    coreID = str(mp.current_process().name[-1])
    print("core {} made it this far; marker{}".format(coreID, 0))

    predictor = Predictor.from_path('https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz')
    print('made it here')
    term_info = term_info
    name = term_info.econ_style_last.replace('.','')
    name = name.replace(' ', '')
    leader_alias_choices = aliases,
    df = chunked_df
    nlp = spacy_nlp_obj

    print("core {} made it this far; marker{}".format(coreID, 1))

    # pbar = tqdm(total = len(chunked_df.index), position = int(mp.current_process().name[-1])-1)
    # pbar.set_description('THREAD: ' + mp.current_process().name[-1] + ' || '+ str(name))

    # Do coreference resolution on that subset of articles that mention the leader

    # for row_index in tqdm(df.index.tolist()):
    for row_index in df.index.tolist():
        print("core {} made it this far; marker{}".format(coreID, 2))
        try:
            pre_resolve_text = df.loc[row_index, 'text']
            print("core {} made it this far; marker{}".format(coreID, 3))
            pred_obj = predictor.predict(document = pre_resolve_text)
            print("core {} made it this far; marker{}".format(coreID, 4))
            spacy_df = pd.DataFrame([], columns = ['text', 'lemma', 'pos', 'tag', 'dep'])

            document_clusters = pred_obj['clusters']    
            document_list = pred_obj['document']
            spacy_doc = nlp(pre_resolve_text) 

            leader_name = leader_alias_choices[0]

            for token in spacy_doc:
                tok_observation = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_]
                spacy_df.loc[len(spacy_df)] = tok_observation

            cluster_of_interest = identifyMainCluster(document_clusters, leader_alias_choices, document_list)

            print("core {} made it this far; marker{}".format(coreID, 5))
            replaced = replaceCoref(leader_name, document_clusters, cluster_of_interest, document_list, spacy_df)
            print("core {} made it this far; marker{}".format(coreID, 6))

            df.loc[row_index, 'resolved_text'] = ' '.join(replaced)
            df.loc[row_index, 'coreference_resolved_ind'] = True
            pbar.update()

        except Exception as e:
            print('excepted')
            print(e)
            df.loc[row_index, 'resolved_text'] = df.loc[row_index, 'text']
            pbar.update()
            continue


        df.loc[row_index, 'pre_in_post_term'] = termLimitChecker(df.loc[row_index, 'date'], term_info.term_start, term_info.term_end)

    return df


# ESTABLISHING MULTIPROCESSING
if __name__ == '__main__':
    #DOING THE PREAMBLE STUFF
    date_index_df = checkDateIndex()
    leaders_windows_indices_df = leaderWindowConstructor(date_index_df)

    LEADER_BATCH_SIZE  = 2
    MAX_NUM_CORES = int(os.environ['SLURM_JOB_CPUS_PER_NODE'])

    # predictor = Predictor.from_path('https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz')
    nlp = spacy.load('en_core_web_sm')


    # Check leaders we have already done
    resolved_leaders_df = pd.read_csv('resolved_leader_tracker_temp.csv')

    non_resolved_leaders_df = pd.merge(leaders_windows_indices_df, resolved_leaders_df, how='outer', on='leadid',indicator=True).query('_merge == "left_only"').drop(columns=['_merge'])



    # SELECTING LEADERS TO RUN THIS INTERATION ON
    # leader_batch_sample = non_resolved_leaders_df.sample(n=LEADER_BATCH_SIZE)
    # leader_batch_sample = non_resolved_leaders_df.loc[non_resolved_leaders_df.ccode == 230]
    leader_batch_sample = non_resolved_leaders_df.loc[non_resolved_leaders_df.leadid == "A2.9-4231"]

    # Run this loop for every leader in this batch
    for index in leader_batch_sample.index.tolist():
        
        term_info = leader_batch_sample.loc[index, :]
        name = term_info.econ_style_last.replace('.','')
        name = name.replace(' ', '')
        leaderid = term_info.leadid.replace('.','')
        leader_gender_hon = term_info.gender
        start_sheet = term_info.start_sheet_num
        end_sheet = term_info.end_sheet_num
        # start_at_0 = True if term_info.issue_starting_row==0 else False


        # Instantiate a list which will contain DFs for future concatenation
        chunk_list = []
        formatted_csv_path = 'formatted_csvs/'
        formatted_csv_stub = 'formatted_sub_article_text'
        suffix = '.csv'

        for sheet_num in range(start_sheet, end_sheet+1):
            chunk_path  = formatted_csv_path + formatted_csv_stub + str(sheet_num) + suffix
            chunk_df = pd.read_csv(chunk_path, parse_dates=['date'], date_parser=custom_date_parser)
            chunk_list.append(chunk_df)

        df = pd.concat(chunk_list, ignore_index=True)


        # Add some extra meta-data to this article-level observation
        # Coerce some of the df[name] observations to True(using a fuzzy match) to identify the subset of all articles in this term +/-6 month window that actually mention the leader
        df['ccode'] = term_info.ccode
        df['country'] = term_info.country
        df['resolved_text'] = ''
        df['pre_in_post_term'] = ''
        df['coreference_resolved_ind'] = False
        df[name] = False

        leader_alias_choices = leaderAliasGenerator(term_info)

        for leader_dummy_idx in tqdm(df.index.tolist(), desc='FUZZY MATCH/SEARCH'):
            string_to_search = df.loc[leader_dummy_idx, 'text']
            df.loc[leader_dummy_idx, name] = fuzzy_leader_search(string_to_search, leader_alias_choices)
        print('after fuzzy match')

        head_length = 8
        df = df[df[name] == True]
        df = df.head(head_length)
        # start_time  = dt.now
        print("number of articles identified for " + name + ": " + str(head_length))
        print("number of cores allocated: {}".format(str(MAX_NUM_CORES)))
        # print("spinning up multiple cores, please be patient")

        # processPool = mp.Pool(MAX_NUM_CORES)
        # print('pool established')
        # df_chunked = np.array_split(df, MAX_NUM_CORES)
        # print('number of df chunks: {}'.format(str(len(df_chunked))))
        

        # compiled = pd.concat(processPool.map(partial(resolverFunc, term_info, leader_alias_choices, nlp), iterable=df_chunked), chunksize=1)
        # processPool.close()
        # processPool.join()

        compiled = resolverFunc(term_info, leader_alias_choices, nlp, df)

        elapsed_time_string = str(dt.now - start_time)
        print('Time to complete {num_articles} coreference resolution with {num_cores} cores: {time}'.format(num_articles=str(head_length), num_cores=str(MAX_NUM_CORES), time=elapsed_time_string))
        
        
        compiled.to_csv('leader_resolved/' + name + '_resolved' + leaderid + 'temp.csv', index=False)
        
        resolved_leaders_df.loc[len(resolved_leaders_df)]=[term_info.leader_x, term_info.leadid, 'RESOLVED']

        resolved_leaders_df.to_csv('resolved_leader_tracker_temp.csv', index=False)









