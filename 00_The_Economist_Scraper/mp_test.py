import pandas as pd
import numpy as np
import multiprocessing as mp
from tqdm import *

from allennlp.predictors.predictor import Predictor
from datetime import datetime as dt
from dateutil.relativedelta import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
import allennlp_models.tagging
import spacy
import re

print('starting')

MAX_NUM_CORES = mp.cpu_count()

# Load in the coreference resolution tool/object


print('here0')


def resolver(df):
    predictor = Predictor.from_path('https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz')

    for index in df.index.tolist():
        print(mp.current_process().name[-1])
        row = df.loc[index, :]
        text = row.pre_resolved_text
        pred_obj = predictor.predict(document = text)

        document_list = pred_obj['document']
        first_10 = ' '.join(document_list[0:10])
        print(first_10)

        return pd.DataFrame({"link": [row.link],
        "resolved_text": [first_10]})
        


if __name__ == '__main__':
    print('here1')

    processPool = mp.Pool(MAX_NUM_CORES)   

    print('here2')
    df = pd.read_csv('mp_test_csv.csv')
    df_chunked = np.array_split(df, MAX_NUM_CORES)
    print('here3')
    print(df_chunked)
    compiled = pd.concat(processPool.map(resolver, df_chunked))
    processPool.close()
    processPool.join()
    print(compiled)
    