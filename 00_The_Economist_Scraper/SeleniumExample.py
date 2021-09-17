from selenium import webdriver
from bs4 import BeautifulSoup
# N.B. This script requires the most up to date version of Chromedriver to work. You can download Chromedriver from this link (YouTube tutorials are available on how/why to do this.): https://chromedriver.chromium.org/

# TO BE REPLACED WITH THE (IMPLICIT OR EXPLICIT) PATH TO YOUR CHROMEDRIVER FILE.
driver = webdriver.Chrome(executable_path = "C:\\Users\\Joshua\\AppData\\Local\\Programs\\Python\\Python38-32\\Scripts\\Selenium Drivers\\chromedriver.exe",)

# IMPORTANT: From the time that the Chromedriver window beings loading the login page, you have 30 seconds to enter your login credentials and use DUO to authenticate. DO NOT close the chrome window once you have done so, the script will do so for you.
driver.maximize_window()

# This should eventually be updated (probably with a for-loop) to access a list/df
url = 'https://www.sec.gov/Archives/edgar/data/1001115/0001193125-18-001659.txt'

# Instructs the Browser to navigate to page specified
driver.get(url)


# Downloads page html and stores it memory.
page = driver.page_source


soup = BeautifulSoup(page, 'html.parser')

# Use the .find() method to find the first element in the source with the "pre" tag. The .text of this tag is a string that appears as the body of the text in the window.
element = soup.find('pre').text
# print(element)

## In this section I was trying to wrap the html string (extracted above) in <html> tags so that BeautifulSoup would interpret it appropriately but I failed. This, in theory, should be doable. Not quite sure what I'm missing here.
open_tag = '<html>'
close_tag = '</html>'
proper_element = open_tag + element + close_tag
print(proper_element)


# These lines don't really work
soup_new = BeautifulSoup(proper_element, 'html.parser')
obj_of_interest = soup_new.find('p',text='Compensation Discussion and Analysis')



# Note that this prints "None" to the console because it was unable to find an element with the <p> tag that also included the string "Compensation Discussion and Analysis"
print(obj_of_interest)
