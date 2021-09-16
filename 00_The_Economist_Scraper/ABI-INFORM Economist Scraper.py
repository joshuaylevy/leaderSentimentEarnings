# Author: Joshua Levy
# Created: 07/28/2021
# Updated: 08/02/2021

# Dependencies/requirements: pandas, BeautifulSoup (bs4), selenium, chromedriver

# N.B. This script requires the most up to date version of Chromedriver to work. You can download Chromedriver from this link (YouTube tutorials are available on how/why to do this.): https://chromedriver.chromium.org/

# IMPORTANT FOR EXECUTION: PLEASE READ THE COMMENT ON LINE XXXXXXXXXXXXXXXXXXXXXXXXX

# General idea of the script: function that first scrapes ABI/INFO for links to every Economist article written since 1992. Then scrape each of those pages for every article. This will be corpus of modern text (1992-present).

import pandas as pd
import numpy as np
import multiprocessing as mp
import re
import sys
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as driverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from functools import partial
from datetime import datetime
from tqdm import *


sys.setrecursionlimit(10**6)
MAX_NUM_CORES = mp.cpu_count()

# To run the entire scraper (collect article links from page and then collect article text) set this to "False". If article links are already locally stored as "article_links.csv" then set this to "True" to just collect article text.
ALL_ARTICLE_LINKS_LOCALLY_STORED = True


# CHANGE THESE PARAMETERS TO CHANGE WHERE TO STOP SCRAPING:
# If you want to scrape up until the end of March, 97. Your parameters should by 1997, 4
END_YEAR = 2021 
END_MONTH  = 1



NUMBER_OF_BATCHES = 10

## This first selenium function exists for two purposes. First it exists to create a suite of authenticated cookies. Doing this with only the requests package is prohibitively cumbersome because of DUO two-factor authentication and because the issue-pages require interaction with the server to load links to each article. Selenium can wait for this to happen and so is better suited to the first part of the collection process.
def cookie_auth_issue_scrape():
    # Initialize pandas df that will store links to each article page (issue/article_date, article_link)
    df_article_links = pd.DataFrame({
        "article_date": [],
        "article_link" : []
        })

    my_options = webdriver.ChromeOptions()
    my_options.add_argument('#enable-webgl')
    my_options.add_argument('#ignore-gpu-blocklist')
    # The executable path should be changed to a path in your own file directory
    driver = webdriver.Chrome(executable_path = "C:\\Users\\Joshua\\AppData\\Local\\Programs\\Python\\Python38-32\\Scripts\\Selenium Drivers\\chromedriver.exe",options = my_options)

    # IMPORTANT: From the time that the Chromedriver window beings loading the login page, you have 30 seconds to enter your login credentials and use DUO to authenticate. DO NOT close the chrome window once you have done so, the script will do so for you.
    driver.maximize_window()

    # This URL gets redirected to a log-in page and then redirected to the first issue page of interest. This is our starting issue: Jan. 4, 1992. We will continue until the , 2021 issue.
    LOGIN_URL = "https://www-proquest-com.proxy.uchicago.edu/abicomplete/publication/41716/citation/83BB1F726DED46D7PQ/6?accountid=14657&decadeSelected=2000%20-%202009&yearSelected=2001&monthSelected=11&issueNameSelected=02001Y11Y03%2423Nov%2B3%2C%2B2001%243b%2B%2BVol.%2B361%2B%24288246%2429"

    driver.get(LOGIN_URL)
    time.sleep(30)

    # Collect all cookies that have been generated in this browser session (i.e. authenticated by user login)
    selenium_cookies = driver.get_cookies()

    # Wait for AJAX to finish so that issue-level details are available and link-scraping can begin
    date_string = nextIssueCheckerWaiter(driver)

    # Collect all the links to the full-text of each article. Put it all in a df and update the existing df
    df_article_links = articleLinkAppender(driver, date_string, df_article_links)

    # Establish where in the timeline we are (do this by reading the URL)
    on_url = driver.current_url
    year = re.search('((?<=yearSelected=)[^&]*)', on_url).group(1)
    month = re.search('((?<=monthSelected=)[^&]*)', on_url).group(1)

    # Proceed to the next issue
    nextIssueClicker(driver)

    end_year = END_YEAR
    end_month = END_MONTH


    while int(year) < end_year or int(month) < end_month:
        time.sleep(1)
        
        # Wait for load and get date-string
        date_string = nextIssueCheckerWaiter(driver)
        tries = 5
        for i in range(tries):
            try:
                # Update where we are in the timeline
                time.sleep(1)
                on_url = driver.current_url
                year = re.search('((?<=yearSelected=)[^&]*)', on_url).group(1)
                month = re.search('((?<=monthSelected=)[^&]*)', on_url).group(1)
            except:
                if i < tries - 1:
                    continue
                else:
                    print('FAILED ON 0:' + on_url)
                    break

        time.sleep(1)
        # Scrape links to articles, update df
        df_article_links = articleLinkAppender(driver, date_string, df_article_links)

        # Proceed to next issue
        if nextIssueClicker(driver) == True:
            continue 
        else:
            #THIS IS WHERE WE SHOULD END 
            break


    driver.quit()

    return selenium_cookies, df_article_links

# Helper function. Waits for things to load and collects some date information. Also, a fail-state checker.
def nextIssueCheckerWaiter(driver):
    tries = 5
    for i in range(tries):
        # Identify if the "Issue Details" header/box has loaded in
        try:
            # Checks every 500ms if the "IssueDetails" header has loaded in. TImes out at 20s and moves on to the finally statement.
            element = driverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "IssueDetails"))
            )

            # If/when it is loaded in, identify the "Issue date/vol/no" capture it, and clean it up
            # Example string: Issue contents: Nov 28, 1992; Vol. 325 (7787)
            # Regex picks up everything between ": " and ";"
            date_string_long = element.text
            date_string = re.search('(?<=: )([^;]*)', date_string_long).group(1)
            return date_string 

        # If you cannot identify that box (i.e. it hasn't loaded in 20s), fail and exit
        except:
            if i < tries - 1:
                continue
            else:
                on_url = driver.current_url
                print("FAILED ON 1: ", on_url)
                break

# Helper function. Click to move on to the next issue
def nextIssueClicker(driver):
    tries = 5
    for i in range(tries):
        try: 
            next_issue_link = driverWait(driver, 20).until(
                EC.visibility_of_element_located((By.LINK_TEXT, 'Next issue'))
            )
            time.sleep(0.5)
            next_issue_link.click()
            return True
        except: 
            if i < tries - 1:
                continue
            else:
                print("Out of new issues: " + driver.current_url)
                return False

# Helper function. Collects all links to articles on an issue page and puts them in a df.
def articleLinkAppender(driver, issue_date, extant_df):
    time.sleep(1)
    tries = 5
    for i in range(tries):
        try:
            # Find every link to the "full text" pages store them in a vector
            full_text_links = driver.find_elements(By.ID, 'addFlashPageParameterformat_fulltext')
            article_links = [lnk.get_attribute('href') for lnk in full_text_links]

            # Assign the vector of links to a df column
            temp_df = pd.DataFrame({
                "article_link" : article_links
            })
            # Give every one of those article-links the date of the current issue
            temp_df["article_date"] = issue_date

            # Append all of this issue's scraped links and dates to all previously scraped
            new_df = pd.concat([extant_df, temp_df])
            return new_df
        except:
            if i < tries - 1:
                continue
            else:
                break
    


# TO BE USED IF LINKS TO ALL ARTICLES HAVE ALREADY BEEN COLLECTED. Read article links out of a locally stored .csv
def articles_from_csv(csv_path):
    article_links_df = pd.read_csv(csv_path)
    return article_links_df

# TO BE USED IF LINKS TO ALL ARTICLES HAVE ALREADY BEEN COLLECTED. Just uses selenium to log you in so that the persistent requests session will have authenticated cookies.
def cookie_auth():

    # The executable path should be changed to a path in your own file directory
    driver = webdriver.Chrome(executable_path = "C:\\Users\\Joshua\\AppData\\Local\\Programs\\Python\\Python38-32\\Scripts\\Selenium Drivers\\chromedriver.exe")

    # IMPORTANT: From the time that the Chromedriver window beings loading the login page, you have 30 seconds to enter your login credentials and use DUO to authenticate. DO NOT close the chrome window once you have done so, the script will do so for you.
    driver.maximize_window()

    # This URL gets redirected to a log-in page and then redirected to the first issue page of interest. This is our starting issue: Jan. 4, 1992. We will continue until the , 2021 issue.
    LOGIN_URL = "https://www-proquest-com.proxy.uchicago.edu/abicomplete/publication/41716/citation/83BB1F726DED46D7PQ/6?accountid=14657&decadeSelected=2020%20-%202029&yearSelected=1992&monthSelected=01&issueNameSelected=01992Y01Y04%2423Jan%2B4%2C%2B1992%243b%2B%2BVol.%2B322%2B%24287740%2429"

    driver.get(LOGIN_URL)
    time.sleep(30)

    selenium_cookies = driver.get_cookies()
    driver.quit()
    return selenium_cookies



# Takes in a list splitted (batch_df /number of cores) df, establishes a single thread and progress tracker. Iterates over that splitted df to scrape article text
def article_scrape_for(cookies, input_df):
    authed_cookies = cookies
    output_df = input_df
    output_df['article_text'] = 'asdf'

    index_object = output_df.index

    pbar = tqdm(total = len(index_object), position = int(mp.current_process().name[-1])-1)
    pbar.set_description('THREAD' + mp.current_process().name[-1])

    for index in output_df.index:
        output_df.loc[index, 'article_text'] = text_scrape(output_df.loc[index,'article_link'], authed_cookies)
        pbar.update()
    return output_df

# Takes in a query for a single article-link (row from splitted df) and returns the text of the article in a single string.
def text_scrape(url, cookies):
    with requests.Session() as session: 
        
        # Passing in authenticated cookies
        REQ_COOKIES = [session.cookies.set(cookie['name'], cookie['value']) for cookie in cookies]
        # Pop session so that we can make more than 40 queries before having to re-authenticate. THIS MUST HAPPEN ON EVERY QUERY (requests.get())
        session.cookies.pop('JSESSIONID')

        tries = 5
        for i in range(tries):
            try:
                page = session.get(url, timeout=(3.05, 20))
                soup = BeautifulSoup(page.content, 'html.parser')
                
                # The body of the article actually lives in paragraphs inside a wrapper. That wrapper has a meta-tag that allows us to identify the wrapper uniquely.
                article_block = soup.find(attrs={'name':'ValidationSchema'}).parent
                article_text_ps = article_block.find_all('p')
                article_text_vect = [element.text for element in article_text_ps]
                article_text_string = '\n'.join(article_text_vect)

                session.cookies.clear()
                # Return the concatenated paragraphs so that the entire body of the article fits in a single cell in a .csv
                return article_text_string

            except: 
                if i < tries - 1:
                    continue
                else:
                    fail_text = "FAILED ON ARTICLE TEXT SCRAPE"
                    # print("FAILED ON 3: " + url)
                    session.cookies.clear()
                    return fail_text


     

if __name__ == '__main__':

    if ALL_ARTICLE_LINKS_LOCALLY_STORED == False:
        # THESE TWO FUNCTIONS ARE TO BE USED IF ARTICLE-LINKS STILL NEED TO BE SCRAPED (This is the "full" run)
        selenium_cookies, article_links_df = cookie_auth_issue_scrape()
        article_links_df.to_csv('article_links.csv', index=False)
        print('number of articles to scrape: ' + str(len(article_links_df.index)))
    else:
        # THESE TWO FUNCTIONS ARE TO BE USED IF ALL ARTICLE-LINKS ARE LOCALLY STORED IN A .CSV (This is a "partial" run)
        selenium_cookies = cookie_auth()
        article_links_df = articles_from_csv('article_links.csv')
        print('number of articles to scrape: ' + str(NUMBER_OF_BATCHES * 1000))



    # # Break the list of links to each article into chunks that will be processed separately by each multicore process
    article_links_df_split = np.array_split(article_links_df, MAX_NUM_CORES)

    tracker = pd.read_csv('tracker_sheet.csv')

    for batch in range(NUMBER_OF_BATCHES):

        # Establish the multicore setup. Note that this will run much faster on machines with lots of logical cores        
        processPool = mp.Pool(MAX_NUM_CORES)

        startTime = datetime.now()
        tracker_sheet_length = len(tracker.index)

        # Identifying some parameters from previous scrapes (stored in the 'tracker_sheet.csv') so that we know where to begin this batch.
        if tracker_sheet_length == 0:
            index_prog = 0
            start_index = 0
            stop_index = 999
        else:
            index_prog = tracker.loc[tracker_sheet_length-1, 'index_prog'] +1
            start_index = tracker.loc[tracker_sheet_length-1, 'article_links_index_start'] + 1000
            stop_index = tracker.loc[tracker_sheet_length-1, 'article_links_index_stop'] + 1000

        out_path = 'sub_csvs/sub_article_text' + str(index_prog) + '.csv'

        # Get the article links to this batch of 1000 articles so that they can be queried.
        sub_df = article_links_df.iloc[start_index : stop_index + 1]

        # Divide that 1000-row batch into (MAX_NUM_CORES) chunks so that each chunk can be scraped in parallel by its own thread.
        sub_df_split = np.array_split(sub_df, MAX_NUM_CORES)


        # Set up the multicore scrape.
        sub_article_text = pd.concat(processPool.map(partial(article_scrape_for, selenium_cookies), sub_df_split))
        processPool.close()
        processPool.join()  

        print('Time to scrape {} observations: {}'.format(len(sub_article_text.index), datetime.now() - startTime) )

        # Update the tracker sheet so that we know where to pick up in the future.
        tracker = tracker.append({'index_prog' : index_prog,
        'article_links_index_start' : start_index,
        'article_links_index_stop': stop_index,
        'sub_article_text_path': out_path}, ignore_index=True)
        tracker.to_csv('tracker_sheet.csv', index=False)

        # Create a sheet for this batch of 1000 queries in the folder named appropriately
        sub_article_text.sort_values('article_date')
        sub_article_text.to_csv(out_path, index=False)










