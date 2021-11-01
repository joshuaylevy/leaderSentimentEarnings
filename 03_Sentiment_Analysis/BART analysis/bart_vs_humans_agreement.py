import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score

BART_scores = pd.read_csv('BART_categorization.csv')

human_scores = pd.read_csv('11-01-21-0915 Human Evaluation.csv')

scores_together = pd.merge(BART_scores, human_scores, how='outer', on='segment_id')



names = ['BART_five', 'luigi', 'tano', 'fabio', 'federico', 'rachel', 'utsav', 'khwaja', 'joshua']
#
scores_together['BART_five'] = scores_together['BART_five'].replace("Very Negative", "Very negative")
scores_together['BART_five'] = scores_together['BART_five'].replace("Very Positive", "Very positive")
#

for name in names:
    print(name)
    scores_together[name] = np.where(scores_together[name] == 'Very positive', 5,
    np.where(scores_together[name] == 'Positive', 4,
    np.where(scores_together[name] == 'Neutral', 3,
    np.where(scores_together[name] == 'Negative', 2,
    np.where(scores_together[name] == 'Very negative', 1, None)))))

scores_together['humans_average_five'] = scores_together.loc[:, ['luigi', 'tano', 'fabio', 'federico', 'rachel', 'utsav', 'khwaja', 'joshua']].mean(axis=1).round()
scores_together['humans_average_five'] = scores_together['humans_average_five'].replace(np.nan, None)
names.append('humans_average_five')

pairwise_names = []
for i in range(len(names)):
    first_name = names[i]
    for j in range(i+1, len(names)):
        second_name = names[j]
        pair_name = '-'.join([first_name, second_name])
        pairwise_names.append(pair_name)



def kappaFunc(row, name1, name2, rater_1_list, rater_2_list):
    rater_1_score = row[name1]
    rater_2_score = row[name2]
    if rater_1_score == None or rater_2_score == None:
        return
    else:
        rater_1_list = rater_1_list.append(rater_1_score)
        rater_2_list = rater_2_list.append(rater_2_score)

for pair in pairwise_names:
    name1 = pair.split('-')[0]
    name2 = pair.split('-')[1]
    rater_1_list = []
    rater_2_list = []
    print(pair)
    scores_together.apply(lambda row, name1=name1, name2=name2, rater_1_list=rater_1_list, rater_2_list=rater_2_list: kappaFunc(row, name1, name2, rater_1_list, rater_2_list), axis=1)

    kappa_stat = cohen_kappa_score(rater_1_list, rater_2_list)
    
    scores_together[pair] = kappa_stat


print(scores_together)

scores_together.to_csv('bart_vs_humans_kappa_stats.csv', index=False)