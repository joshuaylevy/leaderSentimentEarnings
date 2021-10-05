import pandas as pd
import plotly.express as px
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentimentr.sentimentr import Sentiment as sentimentr
from datetime import datetime as dt
from nltk import tokenize
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def leaderFuzzySearch(sentence, name):
    top_set_match = process.extract(sentence, name, scorer=fuzz.token_set_ratio)

    for alias in top_set_match:
        print(alias)
        if alias[1] >= 90:
            return True
        else:
            continue
    return False

leader_of_interest = "gillard"
date_format = '%d-%b-%y'
custom_date_parser = lambda x: dt.strptime(x, date_format)

print(os.getcwd())
resolved_df = pd.read_csv('02_Coreference_Resolution/leader_resolved/gillard_resolved_ccode-900_leadid-A30-218_temp.csv')


resolved_df['article_id'] = resolved_df.reset_index().index
print(len(resolved_df))



sentences_df  = pd.DataFrame([], columns=['article_id', 'sentence'])
for row in resolved_df.index.tolist():
    id = resolved_df.loc[row, 'article_id']
    resolved_text = resolved_df.loc[row, 'resolved_text']
    sentence_list = tokenize.sent_tokenize(resolved_text)
    sentence_df = pd.DataFrame({"sentence" : sentence_list})
    sentence_df['article_id'] = id

    sentences_df = pd.concat([sentences_df, sentence_df], ignore_index=True)

resolved_df = pd.merge(resolved_df, sentences_df, how='left', on='article_id')
resolved_df['leader_sentence_dummy'] = resolved_df.apply(lambda row: "GILLARD" if leader_of_interest in row.sentence.lower() else "OTHER", axis=1)


analyzer = SentimentIntensityAnalyzer()

print(resolved_df['leader_sentence_dummy'].unique())
# print(resolved_df.tail(5))

resolved_df['vader_comp_score'] = resolved_df['sentence'].apply(lambda row: analyzer.polarity_scores(row)['compound'])
resolved_df['sentimentr_comp_score'] = resolved_df['sentence'].apply(lambda row: sentimentr.get_polarity_score(row))
# DIFFERENCE = VADER - SENTIMENTR 
resolved_df['vader_sentimentr_diff'] = resolved_df.vader_comp_score - resolved_df.sentimentr_comp_score 


print(resolved_df.tail(5))

fig = px.scatter(resolved_df, x="date", y="sentimentr_comp_score", color="leader_sentence_dummy")
fig.show()




