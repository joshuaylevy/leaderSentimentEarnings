import pandas as pd
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentimentr.sentimentr import Sentiment as sentimentr
from datetime import datetime as dt
from nltk import tokenize
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#standard fuzzy search to identify sentences that do/n't mention the leader
def leaderFuzzySearch(sentence, name):
    top_set_match = process.extract(sentence, name, scorer=fuzz.token_set_ratio)

    for alias in top_set_match:
        print(alias)
        if alias[1] >= 90:
            return True
        else:
            continue
    return False

#reconstructing the weighted average function used by sentimentr do generate ave_sentiment for sentiment_by
#strongly down-weights netural sentences when aggergating to the entity level
def downweight_zero_mean(x):
    dropped = [num for num in x if pd.isnull(num)==False]
    total_sum = sum(dropped)
    zeros = len([num for num in dropped if num==0])
    non_zeros = len([num for num in dropped if num!=0])

    if zeros == 0:
        downweighted_mean = total_sum /(non_zeros)
        return downweighted_mean
    else:
        try:
            downweighted_mean = total_sum /(non_zeros + math.sqrt(math.log(zeros))) 
            return downweighted_mean
        except:
            downweighted_mean = total_sum / len(dropped)
            return downweighted_mean

leader_of_interest = "gillard"
date_format = '%d-%b-%y'
custom_date_parser = lambda x: dt.strptime(x, date_format)


resolved_df = pd.read_csv('02_Coreference_Resolution/leader_resolved/gillard_resolved_ccode-900_leadid-A30-218_temp.csv')


resolved_df['article_id'] = resolved_df.reset_index().index
print(len(resolved_df))


# Splitting resolved text into sentences (for subsequent sentiment analysis)
sentences_df  = pd.DataFrame([], columns=['article_id', 'sentence'])
for row in resolved_df.index.tolist():
    id = resolved_df.loc[row, 'article_id']
    resolved_text = resolved_df.loc[row, 'resolved_text']
    sentence_list = tokenize.sent_tokenize(resolved_text)
    sentence_df = pd.DataFrame({"sentence" : sentence_list})
    sentence_df['article_id'] = id

    sentences_df = pd.concat([sentences_df, sentence_df], ignore_index=True)

resolved_df = pd.merge(resolved_df, sentences_df, how='left', on='article_id')

# Tag sentences that do/n't mention the leader of interest
resolved_df['leader_sentence_dummy'] = resolved_df.apply(lambda row: "GILLARD" if leader_of_interest in row.sentence.lower() else "OTHER", axis=1)

# Instantiate  VADER's sentiment analysis object (everything gets run through this)
analyzer = SentimentIntensityAnalyzer()


resolved_df['vader_comp_score'] = resolved_df['sentence'].apply(lambda row: analyzer.polarity_scores(row)['compound'])
resolved_df['sentimentr_comp_score'] = resolved_df['sentence'].apply(lambda row: sentimentr.get_polarity_score(row))

# DIFFERENCE = VADER - SENTIMENTR 
resolved_df['vader_sentimentr_diff'] = resolved_df.vader_comp_score - resolved_df.sentimentr_comp_score 


# Aggregate the sentence-level sentiment to the entity-level
entity_level_df = resolved_df.groupby(by=['article_id', 'leader_sentence_dummy', 'date'])['vader_comp_score', 'sentimentr_comp_score'].agg(pd.Series.tolist)
entity_level_df.reset_index(inplace=True)
entity_level_df['vader_comp_score'] = entity_level_df['vader_comp_score'].apply(lambda x: downweight_zero_mean(x))
entity_level_df['sentimentr_comp_score'] = entity_level_df['sentimentr_comp_score'].apply(lambda x: downweight_zero_mean(x))
entity_level_df['vader_sentimentr_diff'] = entity_level_df.vader_comp_score - entity_level_df.sentimentr_comp_score





fig = px.scatter(resolved_df, x="date", y="sentimentr_comp_score", color="leader_sentence_dummy")
fig.show()




