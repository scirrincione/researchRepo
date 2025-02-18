from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import os
import pandas as pd
import time
import re
import xlsxwriter
from datetime import datetime



def get_xlsx(sheet, sheet_name):
    driver=webdriver.Chrome()
    df = pd.read_excel("new_tweet_ids.xlsx", sheet_name=sheet_name)
    rowC = 0
    sheet.write_string(rowC, 0, "ID")
    sheet.write_string(rowC, 1, "tweet")
    sheet.write_string(rowC, 2, "replies")
    sheet.write_string(rowC, 3, "user_handle")
    rowC += 1

    for index,row in df.iterrows():
        if "No tweet found" in row["tweet_id"]:
            continue
        else:
            id = row["tweet_id"]
            target_url = "https://nitter.net/anyuser/status/"+id

            driver.get(target_url)

            resp = driver.page_source
            time.sleep(2)
            soup = BeautifulSoup(resp, 'html.parser')
            handle = soup.find("a", attrs={'class':'username'})
            if handle[1:] != row["user_handle"]:
                continue
            else:
                replies = soup.find_all(attrs={'class':'reply thread thread-line'})
                cleaned_replies = [[line.strip() for line in reply.text.split("\n") if line.strip()] for reply in replies]
                extract_replies = [reply[4] if len(reply) > 4 else reply[-1] for reply in cleaned_replies]
                
                replies_string = "\t".join(extract_replies)
                sheet.write_string(rowC, 0, id)
                sheet.write_string(rowC, 1, row["tweet_text"])
                sheet.write_string(rowC, 2, replies_string)
                rowC += 1
    driver.close()
        
def remove_links(text):
    """
    Remove links along the format 'https://t.co/XBsPQQRGjr' from a string.
    
    :param text: The input string
    :return: The string with links removed
    """
    # Define the regex pattern to match the links
    pattern = r'https://t\.co/\S+'
    
    # Use re.sub() to replace the links with an empty string
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text

def getTweetIDs_xlsx(tweet_workbook, sheet, sheet_name):
    driver=webdriver.Chrome()
    

    df = pd.read_excel("Genuine_Disclosure_Posts/"+sheet_name+".xlsx")
    no_tweet_count = 0
    text_col = 0
    id_col = 1
    user_col = 2
    sheet.write_string(0, text_col, "tweet_text")
    sheet.write_string(0, id_col, "tweet_id")
    sheet.write_string(0, user_col, "user_handle")

    for index, row in df.iterrows():
        text = "\"" + row["tweet_text"] + "\""
        text_formatted = text.replace(" ", "+")
        text_formatted = text_formatted.replace("\n", "")
        text_formatted = text_formatted.replace("@", "%40")
        text_formatted = text_formatted.replace(",", "%2C")
        text_formatted = text_formatted.replace("#", "%23")
        text_formatted = text_formatted.replace("'", "%27")
        text_formatted = text_formatted.replace(";", "%3B")
        text_formatted = remove_links(text_formatted)
        url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "&since=&until=&near="
        

        driver.get(url)

        resp = driver.page_source
        time.sleep(1)
        soup = BeautifulSoup(resp, 'html.parser')
        tweet = soup.find("a", attrs={'class':'tweet-link'})
        handle = soup.find("a", attrs={'class':'profile-card-username'})
        #date = soup.find("div", attrs)
        if tweet is None:
            sheet.write_string(index+1, text_col, row["tweet_text"])
            no_tweet =  "No tweet found "+ str(no_tweet_count)
            sheet.write_string(index+1, id_col, no_tweet)
            sheet.write_string(index+1, user_col, handle[1:])
            no_tweet_count += 1
        else:
            sheet.write_string(index+1, text_col, row["tweet_text"])
            sheet.write(index+1, id_col, extract_tweet_id_regex(tweet['href']))
            sheet.write_string(index+1, user_col, handle[1:])
            
        
    
    driver.close()

def extract_tweet_id_regex(html_string):
    """
    Extract tweet ID using regex pattern matching.
    Looks for numbers between /status/ and #m or end of string
    """
    pattern = r'/status/(\d+)(?:#m)?'
    match = re.search(pattern, html_string)
    return match.group(1) if match else None

def getOneTweet():
    df = pd.read_excel("Genuine_Disclosure_Posts/Australia_Posts.xlsx")
    text = "\"" + df.iloc[5]["tweet_text"] + "\""
    #print(text)
    text_no_spaces = text.replace(" ", "+")
    url = "https://nitter.net/search?f=tweets&q=" + text_no_spaces + "&since=&until=&near="
    
    driver=webdriver.Chrome()

    driver.get(url)
    resp = driver.page_source
    #time.sleep(100)
    driver.close()

    soup = BeautifulSoup(resp, 'html.parser')
    #print(soup.prettify())
    tweet = soup.find("a", attrs={'class':'tweet-link'})
    date = soup.find("div", attrs={'class':'tweet-name-row'})
    date_text = date.text.strip().split('\n')[-1]
    print(date_text)
    print(extract_tweet_id_regex(tweet['href']))

def getUserHandle(userID):
    driver=webdriver.Chrome()
    url = "https://nitter.net/intent/user?user_id="+userID
    driver.get(url)
    resp = driver.page_source
    time.sleep(2)
    driver.close()
    soup = BeautifulSoup(resp, 'html.parser')
    handle = soup.find("a", attrs={'class':'profile-card-username'})
    print(handle.text[1:])

def getUserHandleTweet(tweetID):
    driver=webdriver.Chrome()
    url = "https://nitter.net/anyuser/status/"+tweetID
    driver.get(url)
    resp = driver.page_source
    time.sleep(2)
    driver.close()
    soup = BeautifulSoup(resp, 'html.parser')
    handle = soup.find("a", attrs={'class':'username'})
    print(handle.text[1:])

def get_all_ids():
    tweet_workbook = xlsxwriter.Workbook("new_tweet_ids.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        getTweetIDs_xlsx(tweet_workbook, wsheet, sheet)
    tweet_workbook.close()

def get_all_replies():
    tweet_workbook = xlsxwriter.Workbook("new_tweet_replies.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        get_xlsx(wsheet, sheet)
    tweet_workbook.close()

getUserHandleTweet("1575965103144697856")