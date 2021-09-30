import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime as dt
import re
import os

# Create a "formatted_" folder into which the fixed .csvs will be built 
working_directory = os.getcwd()
print(working_directory)
new_folder_name = "/formatted_csvs/"
new_path = ''.join([working_directory, new_folder_name])
if os.path.exists(new_path):
    print("FORMATTED CSV FOLDER ALREADY EXISTS")
else:
    os.mkdir(new_path)
    print('CREATED NEW /FORMATTED_CSV/ FOLDER')

folder_path = 'sub_csvs/'
file_path = 'sub_article_text'
new_file_path = 'formatted_sub_article_text'
suffix = '.csv'

for file_index in tqdm(range(0, 124)):
    read_in = pd.read_csv(folder_path + file_path + str(file_index) + suffix, quotechar='"', doublequote=True)

    # Instantiate the one-column dataframe
    one_col = pd.DataFrame([], columns =['all_string'])

    # Go row by row through the incorrectly formatted csv and put it all in a single column
    for index in range(len(read_in.index)):
        squeezed = read_in.iloc[index].squeeze()
        listed = []
        for element in squeezed:
            listed.append(element)
        listed_df = pd.DataFrame(listed, columns=['all_string'])
        one_col = pd.concat([one_col, listed_df], ignore_index=True)

    # Drop any NA cells that were identified
    one_col = one_col.dropna()

    # Create a column that identifies a string as an issue-date based on regex: Label for a date-type observation = 1
    # Christmas double-issue editions have a different date format (more on this below)
    one_col['date'] = one_col.apply(lambda row: 1 if re.search('(.*(?=-Jan \d{1,2}))|(\d{1,2}-[A-Za-z]{3}-\d{2})', row.all_string) else 0, axis=1)
    # Create a column that identifies a string as a URL based on regex: Label for a URL-type observation = 2
    one_col['link'] = one_col.apply(lambda row: 2 if re.match('https://www-proquest-com.proxy.uchicago.edu/abicomplete/docview', row.all_string) else 0, axis=1)
    # Create a column that identifies a string as article text (i.e. not a date or link). Label for a text observation = 3.
    one_col['text'] = one_col.apply(lambda row: 3 if((row.date==0) and (row.link==0)) else 0, axis=1)
    # Synthesize
    one_col['label'] = one_col.apply(lambda row: row.date + row.link + row.text, axis=1)

    # Identify the type of string in the row above the current one. I.e. if observation is a link preceded by a piece of text, prev_label=3 (see above)

    one_col['prev_label'] = np.nan

    one_col.reset_index(drop=True, inplace=True)
    for index in range(1, len(one_col)):
        one_col.loc[index, 'prev_label'] = one_col.loc[index-1, 'label']
    one_col.loc[0, 'prev_label'] = 0

    
    # Create a new data frame that will contain:
    formatted = pd.DataFrame([], columns=['date','link','text'])

    # Instantiate helper-vectors
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
            # Need to do some checking of the date format incase its a Christmas issue (different date format)
            date_string = one_col.loc[index, 'all_string']
            match = re.search('(.*(?=-Jan \d{1,2}))|(\d{1,2}-[A-Za-z]{3}-\d{2})', date_string)
            extracted = match[0]
            christmas_format = '%b %d, %Y'
            # COERCE THE EXTRACTED (CHRISTMAS) STRING TO THE REGULAR FORMAT (first date is the publication date)
            try:
                extracted_as_date = dt.strptime(extracted, christmas_format)
                extracted_string_fmt = extracted_as_date.strftime('%d-%b-%y')
                one_col.loc[index, 'all_string'] = extracted_string_fmt
            except:
                # The date is already in the regular format ('%d-%b-%y') so we dont need to coerce it
                pass
            # Append whatever is now in the row of interest (properly formatted now.)
            prep_vect.append(one_col.loc[index, 'all_string'])
        elif row_type == 2:
            #Append the link string (type 2) to the helper vector
            prep_vect.append(one_col.loc[index, 'all_string'])
        elif row_type == 3:
            #Append any text string (type 3) to the text-specific helper vector
            text_prep.append(one_col.loc[index, 'all_string'])

    formatted.to_csv('formatted_csvs/' + new_file_path + str(file_index) + suffix, index=False)

print('COMPLETE')
    