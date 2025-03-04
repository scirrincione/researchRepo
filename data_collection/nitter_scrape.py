from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import xlsxwriter


def get_xlsx(sheet, sheet_name):
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile") 
    chrome_options.add_argument("--profile-directory=SeleniumProfile")  
    driver=webdriver.Chrome(options=chrome_options)
    df = pd.read_excel("final_tweet_ids.xlsx", sheet_name=sheet_name)
    rowC = 0
    sheet.write_string(rowC, 0, "tweet_id")
    sheet.write_string(rowC, 1, "user_handle")
    sheet.write_string(rowC, 2, "tweet")
    sheet.write_string(rowC, 3, "comment_number")
    sheet.write_string(rowC, 4, "retweet_number")
    sheet.write_string(rowC, 5, "quote_number")
    sheet.write_string(rowC, 6, "like_number")
    sheet.write_string(rowC, 7, "replies")

    # Reply format: {handle: xxx, comments: xxx, retweets: xxx, quotes: xxx, likes: xxx, replies: xxx, reply: "xxx"}
    
    rowC += 1

    for index,row in df.iterrows():
        if "No tweet found" in row["tweet_id"] or "No user found" in row["user_handle"]:
            continue
        else:
            id = row["tweet_id"]
            target_url = "https://nitter.net/anyuser/status/"+id

            driver.get(target_url)

            resp = driver.page_source
            time.sleep(3)
            soup = BeautifulSoup(resp, 'html.parser')
            handle_soup = soup.find("div", attrs={'class':'main-tweet'})
            handle = None
            if handle_soup != None:
                handle = handle_soup.find("a", attrs={'class':'username'})
            
            if handle != None and handle.text[1:] != row["user_handle"]:
                continue
            else:
                #main tweet info
                main_soup = soup.find("div", attrs = {'class':'main-tweet'})
                
                if main_soup!=None:
                    stats = main_soup.find_all("span",  attrs = {'class':'tweet-stat'})
                    if stats[0].text == "":
                        sheet.write_string(rowC, 3, "0")
                    else:
                        sheet.write_string(rowC, 3, stats[0].text)
                    if stats[1].text == "":
                        sheet.write_string(rowC, 4, "0")
                    else:
                        sheet.write_string(rowC, 4, stats[1].text)
                    if stats[2].text == "":
                        sheet.write_string(rowC, 5, "0")
                    else:
                        sheet.write_string(rowC, 5, stats[2].text)
                    if stats[3].text == "":
                        sheet.write_string(rowC, 6, "0")
                    else:
                        sheet.write_string(rowC, 6, stats[3].text)

                if soup!=None:
                    replies = soup.find_all(attrs={'class':'reply thread thread-line'})
                
                reply_list = []
                for reply in replies:
                    if reply != None:
                        stats = reply.find_all(attrs={'class':'icon-container'})
                    comment_count = stats[0].text
                    if comment_count == "":
                        comment_count = 0
                    retweet_count = stats[1].text
                    if retweet_count == "":
                        retweet_count = 0
                    quote_count = stats[2].text
                    if quote_count == "":
                        quote_count = 0
                    heart_count = stats[3].text
                    if heart_count == "":
                        heart_count = 0
                    tweet_body = reply.find(attrs={'class':'tweet-content media-body'})
                    handle = reply.find(attrs={'class':'username'})
                    if tweet_body not in replies:
                        reply_list.append(("comment_count", comment_count))
                        reply_list.append(("retweet_count", retweet_count))
                        reply_list.append(("quote_count", quote_count))
                        reply_list.append(("heart_count", heart_count))
                        reply_list.append(("tweet_body", tweet_body.text))
                        reply_list.append(("handle", handle.text[1:]))
                
                sheet.write_string(rowC, 0, id)
                sheet.write_string(rowC, 1, row["user_handle"])
                sheet.write_string(rowC, 2, row["tweet_text"])
                sheet.write_string(rowC, 7, str(reply_list))
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
        url = "https://nitter.net/intent/user?user_id="+str(row["user_id"])
        driver.get(url)
        resp = driver.page_source
        time.sleep(2)
        soup = BeautifulSoup(resp, 'html.parser')
        handle = soup.find("a", attrs={'class':'profile-card-username'})

        text = row["tweet_text"]#"\"" + row["tweet_text"] + "\""
        text_formatted = text.replace(" ", "+")
        text_formatted = text_formatted.replace("\n", "")
        text_formatted = text_formatted.replace("@", "%40")
        text_formatted = text_formatted.replace(",", "%2C")
        text_formatted = text_formatted.replace("#", "%23")
        text_formatted = text_formatted.replace("'", "%27")
        text_formatted = text_formatted.replace(";", "%3B")
        text_formatted = remove_links(text_formatted)
        if handle is not None:
            url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "(from%3A" + handle.text[1:] + ")&since=&until=&near="
        else:
            url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "&since=&until=&near="
        driver.get(url)

        resp = driver.page_source
        time.sleep(2)
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
        if handle is not None:
            sheet.write_string(index+1, user_col, handle.text[1:])
        else:
            sheet.write_string(index+1, user_col, "No user found")
            
        
    
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
    tweet_workbook = xlsxwriter.Workbook("tweet_ids_noq_users.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        getTweetIDs_xlsx(tweet_workbook, wsheet, sheet)
    tweet_workbook.close()

def get_all_replies():
    tweet_workbook = xlsxwriter.Workbook("no_duplicates_tweet_replies.xlsx")
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    for sheet in sheets:
        wsheet = tweet_workbook.add_worksheet(sheet)
        get_xlsx(wsheet, sheet)
    tweet_workbook.close()

def getReplyString(id):
    driver=webdriver.Chrome()
    df = pd.read_excel("final_tweet_ids.xlsx", sheet_name="Australia_Posts")
    
    
    #handle = df.iloc[lineToRead]["user_handle"]
    url = "https://nitter.net/anyuser/status/"+str(id)
    driver.get(url)
    resp = driver.page_source
    time.sleep(1)
    driver.close()
    soup = BeautifulSoup(resp, 'html.parser')
    
    #handle_soup = soup.find("div", attrs={'class':'main-tweet'})
    #found_handle = handle_soup.find("a", attrs={'class':'username'})
    #print("Correct handle: ", handle, " Handle found from tweet: ", found_handle.text[1:])

    main_soup = soup.find("div", attrs = {'class':'replies'})
    comments = main_soup.find_all("div",  attrs = {'class':'reply thread thread-line'})
    for comment in comments:
        print(comment.find("div", attrs = {'class':'tweet-content media-body'}).text)
    
    replies = soup.find_all(attrs={'class':'reply thread thread-line'})
    retweet_count = replies[0].find(attrs={'class':'icon-retweet'})
    tweet = replies[0].find(attrs={'class':'tweet-content media-body'})
    handle = replies[0].find(attrs={'class':'username'})
    comment_count = replies[0].find_all(attrs={'class':'icon-container'})
    print(comment_count[1].text, ", ", tweet.text)
    # Reply formats:
    # This tweet is unavailable (1 item)
    # Name, handle, date, text, comments (optional), reposts (optional), quotes (optional), likes (optional) (4-8 items)

        

def error_check(user_id, tweet_text):
    driver = webdriver.Chrome()
    url = "https://nitter.net/intent/user?user_id="+str(user_id)
    driver.get(url)
    resp = driver.page_source
    time.sleep(2)
    soup = BeautifulSoup(resp, 'html.parser')
    handle = soup.find("a", attrs={'class':'profile-card-username'})

    text = tweet_text#"\"" + tweet_text + "\""
    text_formatted = text.replace(" ", "+")
    text_formatted = text_formatted.replace("\n", "")
    text_formatted = text_formatted.replace("@", "%40")
    text_formatted = text_formatted.replace(",", "%2C")
    text_formatted = text_formatted.replace("#", "%23")
    text_formatted = text_formatted.replace("'", "%27")
    text_formatted = text_formatted.replace(";", "%3B")
    text_formatted = remove_links(text_formatted)
    if handle is not None:
        url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "(from%3A" + handle.text[1:] + ")&since=&until=&near="
    driver.get(url)

    resp = driver.page_source
    time.sleep(2)
    soup = BeautifulSoup(resp, 'html.parser')
    tweet = soup.find("a", attrs={'class':'tweet-link'})
    return (handle.text[1:], tweet)

def get_missing_tweets():
    sheets = ["Australia_Posts", "India_Posts", "Nigeria_Posts", "Philippines_Posts", "South_Africa_Posts", "UK_Posts", "US_Posts"]
    clean_workbook = xlsxwriter.Workbook("final_tweet_ids.xlsx")
    for sheet in sheets:
        driver = webdriver.Chrome()
        tweets = pd.read_excel("tweet_ids_noq_users.xlsx", sheet_name = sheet)
        new_sheet = clean_workbook.add_worksheet(sheet)
        row_count = 0
        new_sheet.write_string(row_count, 0, "tweet_text")
        new_sheet.write_string(row_count, 1, "tweet_id")
        new_sheet.write_string(row_count, 2, "user_handle")
        original_post_sheet = pd.read_excel("Genuine_Disclosure_Posts/"+sheet+".xlsx")
        no_tweet = 0
        print(sheet)
        for index, row in tweets.iterrows():
            row_count += 1
            tweet_text = row["tweet_text"]
            tweet_id = row["tweet_id"]
            user_handle = row["user_handle"]
            if "No tweet found" in tweet_id:
                if "No user found" in user_handle:
                    url = "https://nitter.net/intent/user?user_id="+str(original_post_sheet.iloc[index]["user_id"])
                    driver.get(url)
                    resp = driver.page_source
                    time.sleep(2)
                    soup = BeautifulSoup(resp, 'html.parser')
                    handle = soup.find("a", attrs={'class':'profile-card-username'})
                    if handle is not None:
                        user_handle = handle.text[1:]
                if "No user found" not in user_handle:
                    text = tweet_text
                    text_formatted = text.replace(" ", "+")
                    text_formatted = text_formatted.replace("\n", "")
                    text_formatted = text_formatted.replace("@", "%40")
                    text_formatted = text_formatted.replace(",", "%2C")
                    text_formatted = text_formatted.replace("#", "%23")
                    text_formatted = text_formatted.replace("'", "%27")
                    text_formatted = text_formatted.replace(";", "%3B")
                    text_formatted = remove_links(text_formatted)
                    url = "https://nitter.net/search?f=tweets&q=" + text_formatted + "(from%3A" + user_handle + ")&since=&until=&near="
                    driver.get(url)

                    resp = driver.page_source
                    time.sleep(2)
                    soup = BeautifulSoup(resp, 'html.parser')
                    new_tweet_id = soup.find("a", attrs={'class':'tweet-link'})
                    if new_tweet_id is not None:
                        tweet_id = extract_tweet_id_regex(new_tweet_id['href'])
            if "No tweet found" in tweet_id:
                tweet_id = "No tweet found" + str(no_tweet)
                no_tweet += 1
            new_sheet.write_string(row_count, 0, tweet_text)
            new_sheet.write_string(row_count, 1, tweet_id)
            new_sheet.write_string(row_count, 2, user_handle)
            
    clean_workbook.close()

    
get_all_replies()
#getReplyString(921618405765005312)