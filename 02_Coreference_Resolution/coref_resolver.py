import pandas as pd
from allennlp.predictors.predictor import Predictor
from datetime import datetime as dt
from tqdm import tqdm
import allennlp_models.tagging
import spacy
import re



date_format = '%d-%b-%y'
clinton_date_start = dt.strptime('20-Jan-93', date_format)
clinton_date_end =  dt.strptime('20-Jan-01', date_format)

chunksize = 1000

custom_date_parser = lambda x: dt.strptime(x, date_format)


def identifyMainCluster(clusters, name_vect, document):
    clusters = clusters

    name = ' '.join(name_vect)

    for cluster in clusters:
        for index_pair in cluster:
            start_index = index_pair[0]
            stop_index = index_pair[1]+1
            cluster_as_string = ' '.join(document[start_index:stop_index])

            if (cluster_as_string == name) or (cluster_as_string == name + "\'s"):
                cluster_index = clusters.index(cluster)
                return cluster_index

def replaceCoref(name, clusters, cluster_interest_index, document, tokenized_df):
    name_pos = name[:]
    name_pos[1] = name_pos[1] + "\'s"

    base_cluster = clusters[cluster_interest_index]
    rev_cluster  = sorted(base_cluster, key = lambda x: x[0], reverse = True)

    new_doc_list = document

    df = tokenized_df
    for index_pair in rev_cluster:
        start_index = index_pair[0]
        stop_index = index_pair[1]+1

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

    
    return new_doc_list

def containsPossessive(df, start_index, stop_index):
    possessive_tags = ['POS', 'PRP$']
    cluster_tags = df['tag'].iloc[start_index:stop_index]
    # print(start_index, stop_index)
    # print(df['text'].iloc[start_index:stop_index])
    # print(set(possessive_tags))
    # .isdisjoint returns true if the two sets are disjoin (i.e. do not have any elements interesecting (i.e. does not contain a POS or PRP$)). So negate to return True if "NOT DISJOINT" (CONTAINS POS/PRP$)
    if not set(possessive_tags).isdisjoint(set(cluster_tags)):
        return True
    else:
        return False



chunks = pd.read_csv('formatted_compiled_articles.csv', chunksize=chunksize, parse_dates= ['date'], date_parser=custom_date_parser, nrows=38000)


df = pd.concat(chunks)

df = df[(clinton_date_start <= df.date) & (df.date <= clinton_date_end)]


df['bill_clinton'] = False


for index in tqdm(df.index.tolist()):
    df.loc[index, 'bill_clinton'] = ("Bill Clinton" in df.loc[index, 'text'])


df = df[df.bill_clinton == True]
df = df.head(5)
df['resolved_text'] = ''
df.to_csv('pre_resolution.csv', index=False)


nlp = spacy.load('en_core_web_sm')


predictor = Predictor.from_path('https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz')

for index in tqdm(df.index.tolist()):
    try:
        pre_resolve_text = df.loc[index, 'text']
        pred_obj = predictor.predict(document = pre_resolve_text)

        spacy_df = pd.DataFrame([],columns=['text', 'lemma', 'pos', 'tag', 'dep'])

        document_clusters = pred_obj['clusters']
        document_list = pred_obj['document']
        spacy_doc = nlp(pre_resolve_text)

        name = ['Bill', 'Clinton']
        for token in spacy_doc:
            tok_observation = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_]
            spacy_df.loc[len(spacy_df)] = tok_observation

        cluster_of_interest = identifyMainCluster(document_clusters, name, document_list)

        replaced = replaceCoref(name, document_clusters, cluster_of_interest, document_list, spacy_df)

        df.loc[index, 'resolved_text'] = ' '.join(replaced)
    except:
        df.loc[index, 'resolved_text'] = df.loc[index, 'text']
        continue











df.to_csv('clinton_test.csv', index=False)
