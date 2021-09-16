import pandas as pd
import numpy as np
from tqdm import tqdm
import re

folder_path = 'sub_csvs/'
file_path = 'sub_article_text'
suffix = '.csv'

compiled_df = pd.DataFrame()

for file_index in tqdm(range(0, 124)):
    print('starting to work on: '+ str(file_index))
    read_in = pd.read_csv(folder_path+file_path+str(file_index)+suffix, quotechar='"', doublequote=True)
    # instantiate a pd of a single column that contains all elements of the .csv
    one_col = pd.DataFrame([], columns=['all_string'])

    # Go row by row through the incorrectly formatted csv and put it all in a single column
    for index in range(len(read_in.index)):
        squeezed = read_in.iloc[index].squeeze()
        listed = []
        for element in squeezed:
            listed.append(element)
        listed = pd.DataFrame(listed, columns = ['all_string'])
        one_col = pd.concat([one_col, listed], ignore_index=True)

    #Drop any cells
    one_col = one_col.dropna()

    # Create a column that identifies a string as an issue-date  based on regex: Label for Date = 1
    one_col['date'] = one_col.apply(lambda row: 1 if re.match('\d{1,2}-[A-Za-z]{3}-\d{2}', row.all_string) else 0, axis=1)
    # Create a columnt that identifies a string as a URL based on regex: Label for Link = 2
    one_col['link'] = one_col.apply(lambda row: 2 if re.match('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview', row.all_string) else 0, axis = 1)
    # Create a column that identifies a string as article text (i.e. not a date or link). Label of Text=3
    one_col['text'] = one_col.apply(lambda row: 3 if((row.date == 0) and (row.link == 0)) else 0, axis=1)
    one_col['label'] = one_col.apply(lambda row: row.date + row.link + row.text, axis=1)


    # Identify the type of string in the row above the current one. I.e if observation is a link preceeded by a piece of text, previous label = 3 (see above.)
    one_col['prev_label'] = np.nan

    one_col.reset_index(drop=True,inplace=True)
    for index in range(1,len(one_col)):
        one_col.loc[index, 'prev_label'] = one_col.loc[index-1, 'label']
    one_col.loc[0,'prev_label'] = 0


    # Create a new data frame that will contain 
    formatted = pd.DataFrame([],columns = ['date','link','text'])

    # instantiate helper-vectors
    prep_vect = []
    text_prep = []

    # Passing through row-by-row 
    for index in range(len(one_col)):
        #identify this row's type and the preceeding row's type 
        row_type = one_col.loc[index, 'label']
        prev_type = one_col.loc[index, 'prev_label']

        # if we are at a date-type (type 1) string...
        if row_type == 1:
            #...we should have just finished reading in article text (type 3)
            if prev_type == 3:
                # take all of the article text strings and append them together.
                article_as_string = ' '.join(text_prep)
                # Put that joined string in the vector that will be concatenated with the total
                prep_vect.append(article_as_string)
                try:
                    format_row = pd.DataFrame([prep_vect], columns=['date', 'link', 'text'])
                except:
                    try:
                        prep_vect[2:] = [' '.join(prep_vect[2:])]
                        format_row = pd.DataFrame([prep_vect], columns=['date', 'link', 'text'])
                    except:
                        print('\n' + prep_vect[1] + str(len(prep_vect)) + '\n')

                # Concatenate this row with all previous, cleaned rows
                formatted = pd.concat([formatted, format_row], ignore_index=True)
                # Reset the helper vectors so that they are ready to go on the next row
                prep_vect = []
                text_prep = []
            #Append the date string (type 1) to the helper vector
            prep_vect.append(one_col.loc[index, 'all_string'])
        elif row_type == 2:
            #Append the link string (type 2) to the helper vector
            prep_vect.append(one_col.loc[index, 'all_string'])
        elif row_type == 3:
            #Append any text string (type 3) to the text-specific helper vector
            text_prep.append(one_col.loc[index, 'all_string'])
        
        
    compiled_df = pd.concat([compiled_df, formatted], ignore_index=True)


print(len(compiled_df[compiled_df.text=="asdf"]))
compiled_df.to_csv('formatted_compiled_articles.csv', index=False)