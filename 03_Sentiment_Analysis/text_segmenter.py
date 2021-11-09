import pandas as pd
import numpy as np
import os
import math
from transformers import pipeline
from nltk import tokenize
from dominate import document
from dominate.tags import *

print("STARTING SCRIPT")


#DOCS AND READING:
#https://huggingface.co/facebook/bart-large-mnli
#https://joeddav.github.io/blog/2020/05/29/ZSL.html

articles_vect = [
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1419412733/fulltext/440F7005A3304254PQ/27?accountid=14657', 'leader_resolved/abbott_resolved_ccode-900_leadid-cb-900-2_temp.csv'), #1 ABBOTT
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224003107/fulltext/E4C7C63EED6B4034PQ/51?accountid=14657', 'leader_resolved/harper_resolved_ccode-20_leadid-A30-2_temp.csv'),  #2 HARPER
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/2125590842/fulltext/FBE4209805CA4326PQ/6?accountid=14657', 'leader_resolved/bolsonaro_resolved_ccode-140_leadid-ctb-140-2_temp.csv'), #3 BOLSONARO
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1944465147/fulltext/1AC6F9E48D944371PQ/8?accountid=14657', 'leader_resolved/macron_resolved_ccode-220_leadid-se-220-2_temp.csv'), #4 MACRON
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224060439/fulltext/E52D8BF939B14E93PQ/25?accountid=14657', 'leader_resolved/obuchi_resolved_ccode-740_leadid-A29-8200_temp.csv'), #5 OBUCHI
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1641939120/fulltext/C69F63FFC27C44F4PQ/3?accountid=14657', 'leader_resolved/tsipras_resolved_ccode-350_leadid-cb-350-3_temp.csv'), #6 TSIPRAS TERM 1
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224043446/fulltext/F450D1B8DB1D4D38PQ/14?accountid=14657', 'leader_resolved/orban_resolved_ccode-310_leadid-A29-4561_temp.csv'), # 7 ORBAN
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/223985023/fulltext/B9FA3B18EA24D07PQ/42?accountid=14657', 'leader_resolved/zapatero_resolved_ccode-230_leadid-A29-4234_temp.csv'), # 8 ZAPATERO
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224087050/fulltext/678A1258C4E841BDPQ/27?accountid=14657', 'leader_resolved/shipley_resolved_ccode-920_leadid-A29-9064_temp.csv'), # 9 SHIPLEY
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224044687/fulltext/24081F79A2FC4CE0PQ/41?accountid=14657', 'leader_resolved/stoltenberg_resolved_ccode-385_leadid-A29-6061_temp.csv'), # 10 STOLTENBERG
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224054311/fulltext/5016477739164CB7PQ/37?accountid=14657', 'leader_resolved/schroder_resolved_ccode-255_leadid-A29-4378_temp.csv'), # 11 SCHRODER
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/2451166210/fulltext/A5C7463A8C034C7CPQ/46?accountid=14657', 'leader_resolved/modi_resolved_ccode-750_leadid-cb-750-1_temp.csv'), # 12 MODI
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1905049012/fulltext/19AEACB884A247BAPQ/18?accountid=14657', 'leader_resolved/kern_resolved_ccode-305_leadid-se-305-2_temp.csv'), # 13 KURZ
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224017780/fulltext/6B716A15E98E4AFAPQ/10?accountid=14657', 'leader_resolved/singh_resolved_ccode-750_leadid-A29-8260_temp.csv'), # 14 SINGH
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1024951461/fulltext/8CCB6E6BF51F4C98PQ/34?accountid=14657', 'leader_resolved/noda_resolved_ccode-740_leadid-A30-188_temp.csv'), # 15 NODA
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/2053219416/fulltext/D88A0C6A813A4872PQ/19?accountid=14657', 'leader_resolved/rajoy_resolved_ccode-230_leadid-A30-57_temp.csv'), # 16 RAJOY
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1505353521/fulltext/7CCDABAD333B48BAPQ/54?accountid=14657', 'leader_resolved/hollande_resolved_ccode-220_leadid-cb-220-1_temp.csv'), # 17 HOLLANDE
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/1936701314/fulltext/DF1F2E64042A4068PQ/4?accountid=14657', 'leader_resolved/merkel_resolved_ccode-255_leadid-A30-59_temp.csv'), # 18 MERKEL
    ('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview/224112657/fulltext/44DDDC146AF4474FPQ/52?accountid=14657', 'leader_resolved/cardoso_resolved_ccode-140_leadid-A29-2053_temp.csv'), # 19 CARDOSO

]

df = pd.DataFrame()

for article in articles_vect:
    print(article[1])
    search_df = pd.read_csv(article[1])
    print(article[0])
    row = search_df[search_df.link == article[0]]
    print(row)
    df = pd.concat([df, row], ignore_index=True)


df = df[['text', 'link']]

peru_article_string = '''Peru
LIMA
So far Pedro Castillo's presidency is one of trial, error and infighting
When he took office as Peru's president on July 28th, the bicentenary of the country's independence, Pedro Castillo declared that he would not govern from the presidential palace. Built on the site of the house of Francisco Pizarro, the Spanish conquistador, the palace is a "colonial symbol", he said, which he would turn into a museum. Three months later President Castillo is quietly living and working there after all. It is a sign that whatever Peru's hard-left president might like, the country is not in the throes of revolution.
Rather Mr Castillo's presidency has been defined so far by his political inexperience and indecision, the extremism and infighting of his allies and his weak mandate. A rural schoolteacher, farmer and union activist from a small town in the Andes who had never before held political office, his victory by just 44,000 votes out of 17.5m was a surprise. For his supporters he represents both the Peru that has not shared fully in the country's economic growth and a provincial rebellion against Lima, the capital. He won because politics has fragmented, because the pandemic exposed injustice and neglect and because many Peruvians could not bring themselves to vote for his opponent, Keiko Fujimori, a conservative whose father ruled the country as a corrupt autocrat in the 1990s.
Mr Castillo wasted his first nine weeks in office, appointing a dysfunctional cabinet of the far left that many Peruvians saw as an affront. His own political base is of radical teachers, many close to the former Maoist terrorists of the Shining Path. Police records suggested that the labour minister may have taken part in terrorist attacks. Vladimir Cerrón, the boss of Perú Libre (Free Peru), the party under whose banner Mr Castillo ran, is a Cuban-trained Leninist doctor. Mr Cerrón tried to co-govern through Guido Bellido, his nominee as Mr Castillo's first prime minister, an agitator who publicly countermanded any sign of moderation from the president. Mr Cerrón and Mr Castillo both want a constituent assembly, the device through which other leftist Latin American presidents have imposed authoritarian regimes.
With the government destabilising itself, the currency depreciated daily, pushing up inflation (to 5.2% over the past year). The opposition-controlled Congress began to murmur of impeachment. In early October Mr Castillo "decided to take some decisions in favour of governability", as he put it.
For a start, he replaced Mr Bellido with Mirtha Vásquez, a human-rights lawyer and former speaker of Congress. Although she has leftist convictions, she is seen as realistic and consensual. Of a constituent assembly, she said the government "is not going to propose this for tomorrow" and that its priorities were vaccination, reopening schools and economic recovery. At the same time Mr Castillo reappointed Julio Velarde, the respected central-bank president, for a fourth five-year term. That calmed the currency market. "We are leftwing, but we are not going to do crazy things," insists Pedro Francke, the economy minister.
The new cabinet is only a marginal im- ?? t provement. The interior minister is a former policeman with a string of (unfair, he says) disciplinary reprimands. As a lawyer he has represented arms traffickers as well as Mr Cerrón (who was convicted of corruption). Only four or five ministers have a reputation for competence. But at least Mr Castillo has bought some time.
Can he use it to achieve change that benefits poorer Peruvians? The government wants to expand tax revenues from 15% of gdp to 17%, to spend more on health care, education and family farming. Mr Francke sees scope to raise taxes on mining companies, which are enjoying high prices, and to crack down on evasion. He has asked the World Bank and the imf to advise on tax reform "so that it's not anti-competitive". Whereas Mr Bellido had threatened to nationalise the Camisea natural-gas field, Ms Vásquez's team is studying ways to build pipelines so that more Peruvians can benefit from it.
Brothers in arms, and government
Mr Castillo faces two big problems. He mistrusts "technocracy, the market, business people and Lima", says an official who has dealt with him. He shuns the media, preferring rallies with his base in the interior. That mistrust is reciprocated. Many in private business are alarmed, especially by the threat of a constituent assembly. While output has already recovered from last year's slump (though employment has not), lack of confidence means that Peru will be lucky if its economy grows by 3% next year. Lima's once-booming property market is dead. Capital and business people are leaving the country.
The second problem is that the government's diagnosis of Peru's difficulties is mistaken. It is not the market economy that has failed but an inefficient state. Tax collection is low because 70% of Peruvians work informally. In many ministries, Mr Castillo's team are placing supporters in senior posts for which they are unqualifled. That has happened in the social-development ministry, which has a big role to play in ensuring that the 3m Peruvians who fell into poverty last year get out of it. The new education minister is a friend of Mr Castillo, and a former teacher, who wants to repeal a successful reform that requires teachers to be subjected to evaluation and paid according to performance.
Mr Castillo and his supporters reject the idea of ending up like Ollanta Humala, a former president who campaigned as a radical leftist but presided over a mildly social democratic government. Yet that may be the only way for Mr Castillo to survive for five years. "The country is so complicated, there's no space for their more radical proposals," says Miguel Castilla, who was Mr Humala's economy minister. It looks likely to become even more complex.'''


peru_df = pd.DataFrame({'text' : peru_article_string, 'link': 'https://www.proquest.com/abicomplete/docview/2584785374/C16719CA97D544F0PQ/33?accountid=14657'}, index=[0])

print('here')

df = df.append(peru_df, ignore_index=True)


df['article_id'] = df.reset_index().index

resolutions_df = pd.DataFrame([], columns=['article_id','text', 'para_id', 'para_text', 'sentence_text'])
for row in df.index.tolist():
    id = df.loc[row, 'article_id']
    a_id = "A{}".format(id)
    text = df.loc[row, 'text']

    if row == 19:
        text = text.replace('\n', '\r\n')
    paragraph_list = text.split('\r\n')

    print(len(paragraph_list))

    para_df = pd.DataFrame([], columns=['article_id','para_id', 'para_text', 'sentence_text', 'sentence_id'])
    for i in range(len(paragraph_list)):
        paragraph_id = "{}-P{}".format(a_id, i)
        paragraph_text = paragraph_list[i]
        sentence_list = tokenize.sent_tokenize(paragraph_text)
        sentence_df = pd.DataFrame({'sentence_text': sentence_list})
        sentence_df.reset_index()
        sentence_df['sentence_id'] = ""
        for j in sentence_df.index.tolist():
            sentence_df.loc[j, 'sentence_id'] = "{}-S{}".format(paragraph_id, j) 
        sentence_df['para_id'] = paragraph_id
        sentence_df['para_text'] = paragraph_text
        sentence_df['article_id'] = a_id

        para_df = pd.concat([para_df, sentence_df], ignore_index=True)

    para_df['text'] = text

    resolutions_df = pd.concat([resolutions_df, para_df], ignore_index=True)





segments_df = resolutions_df.set_index(['article_id', 'para_id', 'sentence_id']).stack().reset_index().rename(columns={'level_3': 'type', 0: 'text_segment'})

segments_df = segments_df.drop_duplicates(subset=['article_id','type', 'text_segment'])

segments_df['segment_id'] = np.where(segments_df.type == "text", segments_df.article_id,
    (np.where(segments_df.type == "para_text", segments_df.para_id, segments_df.sentence_id))
)

segments_df = segments_df.drop(columns=['article_id', 'para_id', 'sentence_id'])

segments_df.to_csv('segmentation_out.csv', index=False)



classifier = pipeline("zero-shot-classification")
labels = ['Positive', 'Neutral', 'Negative']

resolutions_df['sentence_positive'] = np.nan
resolutions_df['sentence_neutral'] = np.nan
resolutions_df['sentence_negative'] = np.nan
resolutions_df['para_positive'] = np.nan
resolutions_df['para_neutral'] = np.nan
resolutions_df['para_negative'] = np.nan
resolutions_df['article_positive'] = np.nan
resolutions_df['article_neutral'] = np.nan
resolutions_df['article_negative'] = np.nan


def classifierFunction(resolutions_df, text_type, input_index, input_text, class_labels):
    scored = classifier(
        input_text,
        candidate_labels=class_labels
    )

    labels = scored['labels']
    scores = scored['scores']
    print(text_type)
    print(input_index)
    print(labels)
    print(scores)

    tp = text_type
    type_id = lambda tp: tp + '_id' if tp=="article" or tp=="para" else tp + '_text'


    cols_na_check =['article_positive','article_neutral','article_negative','para_positive','para_neutral','para_negative','sentence_positive','sentence_neutral','sentence_negative']
    
    for i in range(len(labels)):
        label = labels[i]
        score = scores[i]

        if label == 'Positive':
            type_sent = tp + '_positive'
            resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, type_sent] = scores[i]
            # print(resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, cols_na_check])
        elif label == 'Neutral':
            type_sent = tp + '_neutral'
            resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, type_sent] = scores[i]
            # print(resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, cols_na_check])
        else:
            type_sent = tp + '_negative'
            resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, type_sent] = scores[i]
            # print(resolutions_df.loc[resolutions_df[type_id(tp)] == input_index, cols_na_check])

    return


for sentence in resolutions_df.index.tolist():
    sentence_text = resolutions_df.loc[sentence, 'sentence_text']
    paragraph_id = resolutions_df.loc[sentence, 'para_id']
    article_id = resolutions_df.loc[sentence, 'article_id']

    # print(sentence_text)
    # print(paragraph_id)
    # print(article_id)

    classifierFunction(resolutions_df, 'sentence', sentence_text, sentence_text, labels)

paragraphs_df = resolutions_df.drop_duplicates(subset=['para_id'])
for paragraph in paragraphs_df.index.tolist():
    paragraph_text = paragraphs_df.loc[paragraph, 'para_text']
    paragraph_id  = paragraphs_df.loc[paragraph, 'para_id']
    article_id = paragraphs_df.loc[paragraph, 'article_id']

    # print(paragraph_text)
    # print(paragraph_id)
    # print(article_id)

    classifierFunction(resolutions_df, 'para', paragraph_id, paragraph_text, labels)   

articles_df = resolutions_df.drop_duplicates(subset=['article_id'])
for article in articles_df.index.tolist():
    article_text = articles_df.loc[article, 'text']
    article_id = articles_df.loc[article, 'article_id']

    # print(article_text)
    # print(article_id)

    classifierFunction(resolutions_df, 'article', article_id, article_text, labels)


###################################
#### COLORING FOR HTML OUTPUT ##### 
###################################


def colorGen(positive, neutral, negative, color_grades):
    scores_dict = {
        "positive_score" : positive,
        "neutral_score" : neutral,
        "negative_score" : negative
    }

    colors_dict = {
    "very_negative" : "rgb(224,102,102)",
    "negative" : "rgb(244,199,195)",
    "neutral" : "rgb(252,232,179)",
    "positive" : "rgb(183,225,205)",
    "very_positive" : "rgb(106,168,79)"
    }   
    interval_width = (1 - 1/3)/2 
    reg_lower = 1/3
    reg_very_bound = 1/3 + interval_width

    scores_list = list(scores_dict.values())
    scores_dict_keys = list(scores_dict.keys())
    max_score = max(scores_list)
    max_score_index = scores_list.index(max_score)
    max_score_key_full = scores_dict_keys[max_score_index]
    max_score_key = max_score_key_full.split('_')[0]
    # print("----------------------")
    # print("SCORES LIST: {}".format(scores_list))
    # print("SCORES DICTIONARY KEYS: {}".format(scores_dict_keys))
    # print("MAX SCORE: {}".format(max_score))
    # print("MAX SCORE INDEX: {}".format(max_score_index))
    # print("MAX SCORE KEY: {}".format(max_score_key))
    # print("----------------------")


    if color_grades == "three_color":
    
        rgb_string = colors_dict.get(max_score_key)
        # print(rgb_string)
        return rgb_string

    elif color_grades == "five_color":

        if reg_lower < max_score <= reg_very_bound:
            rgb_string = colors_dict.get(max_score_key)

        elif reg_very_bound <= max_score <= 1:
            if max_score_key == "neutral":
                rgb_string = colors_dict.get(max_score_key)
            else:            
                rgb_string = colors_dict.get("very_" + max_score_key)
        
        print(rgb_string)
        return rgb_string

    elif color_grades == "smooth_colors":
        positive_val = math.floor(100 + (positive * 155))
        neutral_val = math.floor(100 + (neutral * 155))
        negative_val = math.floor(100 + (negative * 155))

        rgb_string = "rgb({}, {},{})".format(negative_val, positive_val, neutral_val)
        return rgb_string

with document(title="BART SCORING") as doc:
    for article in articles_df.index.tolist():
        article_positive = resolutions_df.loc[article, 'article_positive']
        article_neutral = resolutions_df.loc[article, 'article_neutral']
        article_negative = resolutions_df.loc[article, 'article_negative']

        article_id =  resolutions_df.loc[article, 'article_id']
        article_score_vector = ["Positive:", str(article_positive), "Neutral:", str(article_neutral), "Negative:", str(article_negative)]
        
        h2("ARTICLE SCORES: {}".format(' '.join(article_score_vector)), cls="article-id-{}".format(article_id))
        print(article_id)

        for para in resolutions_df.loc[resolutions_df.article_id == article_id, 'para_id'].drop_duplicates().index.tolist():
            para_id = resolutions_df.loc[para, 'para_id']
            print("Paragraph_id: {}".format(para_id))

            para_positive = resolutions_df.loc[para, 'para_positive']
            para_neutral = resolutions_df.loc[para, 'para_neutral']
            para_negative = resolutions_df.loc[para, 'para_negative']

            with div():
                p_border_color_string = colorGen(para_positive, para_neutral, para_negative, "five_color")
                attr(cls='paragraph', style="border-color: {}; border-style: solid;  border-width: thick".format(p_border_color_string))

                for sentence in resolutions_df.loc[(resolutions_df.article_id == article_id) & (resolutions_df.para_id == para_id), 'sentence_text'].index.tolist():
                    sentence_positive = resolutions_df.loc[sentence, 'sentence_positive']
                    sentence_neutral = resolutions_df.loc[sentence, 'sentence_neutral']
                    sentence_negative = resolutions_df.loc[sentence, 'sentence_negative']
                    
                    s_background_color_string = colorGen(sentence_positive, sentence_neutral, sentence_negative, "five_color")
                    sentence_text = resolutions_df.loc[sentence, 'sentence_text']

                    span(sentence_text, style="background-color: {}".format(s_background_color_string))


with open('BART_SCORING_FIVE_COLORS.html', 'w') as f:
    f.write(doc.render())


###################################
## CATEGORIZATION FOR AGREEMENT ### 
###################################
categorical_df = resolutions_df.set_index(['article_id', 'para_id', 'sentence_id', 'article_positive', 'article_neutral', 'article_negative', 'para_positive', 'para_neutral', 'para_negative', 'sentence_positive', 'sentence_neutral', 'sentence_negative']).stack().reset_index().rename(columns={'level_12': 'type', 0: 'text_segment'})



print(categorical_df)
print(categorical_df.columns)


categorical_df = categorical_df.drop_duplicates(subset=['article_id', 'type', 'text_segment'])

categorical_df['segment_id'] = np.where(categorical_df.type == "text", categorical_df.article_id, (np.where(categorical_df.type == "para_text", categorical_df.para_id, categorical_df.sentence_id)))

categorical_df.drop(columns=['article_id', 'para_id', 'sentence_id'])

def catFunc(row, num_cat):
    segment_type = row['type']
    interval_width = (1 - 1/3)/2 
    reg_lower = 1/3
    reg_very_bound = 1/3 + interval_width

    if segment_type == "text":
        scores_dict = {
            "Positive_BART" : row['article_positive'],
            "Neutral_BART" : row['article_neutral'],
            "Negative_BART" : row['article_negative']
        }
    elif segment_type == "para_text":
        scores_dict = {
            "Positive_BART" : row['para_positive'],
            "Neutral_BART" : row['para_neutral'],
            "Negative_BART" : row['para_negative']
        }
    else:
        scores_dict = {
            "Positive_BART" : row['sentence_positive'],
            "Neutral_BART" : row['sentence_neutral'],
            "Negative_BART" : row['sentence_negative']
        }

    scores_list = list(scores_dict.values())
    scores_dict_keys = list(scores_dict.keys())
    max_score = max(scores_list)
    max_score_index = scores_list.index(max_score)
    max_score_key_full = scores_dict_keys[max_score_index]
    max_score_key = max_score_key_full.split('_')[0] 

    if num_cat == 'three':
        three_cat_sent_val = max_score_key
        return three_cat_sent_val
    
    if num_cat == 'five':

        if max_score_key == "Neutral":
            five_cat_sent_val = "Neutral"
        else:
            if reg_lower < max_score <= reg_very_bound:
                five_cat_sent_val = max_score_key
            else:
                five_cat_sent_val = "Very " + max_score_key.lower()
        return five_cat_sent_val
    
categorical_df['three_cat_sent'] = categorical_df.apply(lambda row: catFunc(row, 'three'), axis=1)
categorical_df['five_cat_sent'] = categorical_df.apply(lambda row: catFunc(row, 'five'), axis=1)

for row in categorical_df.index.tolist():
    segment_type = categorical_df.loc[row, 'type']
    if segment_type == 'text':
        for col in ['para_positive', 'para_neutral', 'para_negative', 'sentence_positive', 'sentence_neutral', 'sentence_negative']:
            categorical_df.loc[row, col] = np.nan

    elif segment_type == 'para_text':
        for col in ['article_positive', 'article_neutral', 'article_negative', 'sentence_positive', 'sentence_neutral', 'sentence_negative']:
            categorical_df.loc[row, col] = np.nan
    else:
        for col in ['article_positive', 'article_neutral', 'article_negative', 'para_positive', 'para_neutral', 'para_negative']:
            categorical_df.loc[row, col] = np.nan

categorical_df = categorical_df.rename(columns={'three_cat_sent' : 'BART_three', 'five_cat_sent' : 'BART_five'})
categorical_df = categorical_df.drop(columns=['article_id', 'para_id', 'sentence_id'])

categorical_df.to_csv('BART_categorization.csv',index=False)