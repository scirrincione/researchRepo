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
    df = pd.read_excel("tweet_ids.xlsx", sheet_name=sheet_name)
    rowC = 0
    sheet.write_string(rowC, 0, "ID")
    sheet.write_string(rowC, 1, "tweet")
    sheet.write_string(rowC, 2, "replies")
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
    
            replies = soup.find_all(attrs={'class':'reply thread thread-line'})
            cleaned_replies = [[line.strip() for line in reply.text.split("\n") if line.strip()] for reply in replies]
            extract_replies = [reply[4] if len(reply) > 4 else reply[-1] for reply in cleaned_replies]
            
            replies_string = "\t".join(extract_replies)
            sheet.write_string(rowC, 0, id)
            sheet.write_string(rowC, 1, row["tweet_text"])
            sheet.write_string(rowC, 2, replies_string)
            rowC += 1
    driver.close()

def get_csv():
    driver=webdriver.Chrome()
    if os.path.exists("tweets.csv"):
        os.remove("tweets.csv")
    with open("tweets.csv", "w", newline = "") as pf:
        writer = csv.writer(pf)
        writer.writerow(["ID", "main_tweet", "reply_list"])
        with open("tweet_ids.csv", "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                if line == None or "No tweet found" in line:
                    continue
                else:
                    id = line.rsplit(',',1)[-1]
                    print(id)
                    target_url = "https://nitter.net/anyuser/status/"+id

                    driver.get(target_url)

                    resp = driver.page_source
                    

                    soup = BeautifulSoup(resp, 'html.parser')

            
                    tweet = soup.find("div", id="m")
                    cleaned_tweet = [line.strip() for line in tweet.text.split("\n") if line.strip()]
                    replies = soup.find_all(attrs={'class':'reply thread thread-line'})
                    cleaned_replies = [[line.strip() for line in reply.text.split("\n") if line.strip()] for reply in replies]
                    print(cleaned_replies)
                    extract_replies = [reply[4] for reply in cleaned_replies]
                    writer.writerow([id,cleaned_tweet[3],extract_replies])
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
    date_col = 2
    sheet.write_string(0, text_col, "tweet_text")
    sheet.write_string(0, id_col, "tweet_id")

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
        #date = soup.find("div", attrs)
        if tweet is None:
            sheet.write_string(index+1, text_col, row["tweet_text"])
            no_tweet =  "No tweet found "+ str(no_tweet_count)
            sheet.write_string(index+1, id_col, no_tweet)
            no_tweet_count += 1
        else:
            sheet.write_string(index+1, text_col, row["tweet_text"])
            sheet.write(index+1, id_col, extract_tweet_id_regex(tweet['href']))
            
        
    
    driver.close()

def workbookTests():
    workbook = xlsxwriter.Workbook('test.xlsx')
    worksheet = workbook.add_worksheet()
    df = pd.read_excel("Genuine_Disclosure_Posts/Australia_Posts.xlsx")
    for index, row in df.iterrows():
        worksheet.write_string(index, 0, row["tweet_text"])
    workbook.close()

def getTweetIDs():
    driver=webdriver.Chrome()
    if os.path.exists("tweet_ids.csv"):
        os.remove("tweet_ids.csv")
    with open("tweet_ids.csv", "w", newline = "") as pf:
        writer = csv.writer(pf)
        writer.writerow(["tweet_text", "tweet_id"])
        df = pd.read_excel("Genuine_Disclosure_Posts/Australia_Posts.xlsx")
        no_tweet_count = 0
        for index, row in df.iterrows():
            text = "\"" + row["tweet_text"] + "\""
            text_formatted = text.replace(" ", "+")
            text_formatted = text_formatted.replace("\n", "")
            text_formatted = text_formatted.replace("@", "%40")
            text_formatted = text_formatted.replace(",", "%2C")
            text_formatted = text_formatted.replace("#", "%23")
            text_formatted = text_formatted.replace("'", "%27")
            text_formatted = text_formatted.replace(";", "%3B")
            text_formatted = text_formatted.replace("&", "%26")
            url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "&since=&until=&near="
            

            driver.get(url)

            resp = driver.page_source

            soup = BeautifulSoup(resp, 'html.parser')
            tweet = soup.find("div", attrs={'class':'tweet-link'})
            tweet = soup.find("a", attrs={'class':'tweet-link'})

            if tweet is None:
                writer.writerow([row["user_id"], "No tweet found "+str(no_tweet_count)])
                no_tweet_count += 1
            else:
                writer.writerow([row["user_id"], extract_tweet_id_regex(tweet['href'])])
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

def get_all_ids():
    tweet_workbook = xlsxwriter.Workbook("tweet_ids.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        getTweetIDs_xlsx(tweet_workbook, wsheet, sheet)
    tweet_workbook.close()

def get_all_replies():
    tweet_workbook = xlsxwriter.Workbook("tweet_replies.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        get_xlsx(wsheet, sheet)
    tweet_workbook.close()

getOneTweet()