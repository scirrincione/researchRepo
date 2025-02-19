from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import os
import pandas as pd
import time
import re
import xlsxwriter
from datetime import datetime
from dog_scrape import extract_tweet_id_regex

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

def getTweetIDs():
    driver=webdriver.Chrome()
    if os.path.exists("tweet_ids.csv"):
        os.remove("tweet_ids.csv")
    with open("tweet_ids.csv", "w", newline = "") as pf:
        writer = csv.writer(pf)
        writer.writerow(["tweet_text", "tweet_id", "real_user_handle"])
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
            handle = soup.find("a", attrs={'class':'profile-card-username'})

            if tweet is None:
                writer.writerow([row["user_id"], "No tweet found "+str(no_tweet_count)])
                no_tweet_count += 1
            else:
                writer.writerow([row["user_id"], extract_tweet_id_regex(tweet['href']), handle.text[1:]])
    driver.close()

def workbookTests():
    workbook = xlsxwriter.Workbook('test.xlsx')
    worksheet = workbook.add_worksheet()
    df = pd.read_excel("Genuine_Disclosure_Posts/Australia_Posts.xlsx")
    for index, row in df.iterrows():
        worksheet.write_string(index, 0, row["tweet_text"])
    workbook.close()