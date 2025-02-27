import requests
import json
import csv
import os


if os.path.exists("tweets.csv"):
    os.remove("tweets.csv")

def create_csv():
    with open("tweets.csv", "w", newline = "") as pf:
        writer = csv.writer(pf)
        writer.writerow(["Username", "Tweet", "Date", "Replies", "Retweets", "Likes"])
        with open('usernames.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                username = line.strip()
                url = "https://syndication.twitter.com/srv/timeline-profile/screen-name/" + username

                r = requests.get(url)

                html = r.text
                print(html)
                start_str = '<script id="__NEXT_DATA__" type="application/json">'
                end_str = '</script></body></html>'

                start_index = html.index(start_str) + len(start_str)
                end_index = html.index(end_str, start_index)

                json_str = html[start_index: end_index]
                data = json.loads(json_str)
                #print(data["props"]["pageProps"]["timeline"]["entries"][1]["content"]["tweet"]["full_text"])
            
                for tweet in data["props"]["pageProps"]["timeline"]["entries"]:
                    tweet_text = tweet["content"]["tweet"]["full_text"]
                    clean_tweet = tweet_text.replace("\n", " ")

                    date = tweet["content"]["tweet"]["created_at"]
                    
                    replies = tweet["content"]["tweet"]["reply_count"]

                    retweet = tweet["content"]["tweet"]["retweet_count"]

                    likes = tweet["content"]["tweet"]["favorite_count"]
                    writer.writerow([username,clean_tweet,date,replies,retweet,likes])

def json_dump():
    username = "jarvis"
    url = "https://syndication.twitter.com/srv/timeline-profile/screen-name/"+username
    
    r = requests.get(url)

    html = r.text
    
    start_str = '<script id="__NEXT_DATA__" type="application/json">'
    end_str = '</script></body></html>'

    start_index = html.index(start_str) + len(start_str)
    end_index = html.index(end_str, start_index)

    json_str = html[start_index: end_index]
    data = json.loads(json_str)

    #print(data["props"]["pageProps"]["timeline"]["entries"][1]["content"]["tweet"]["full_text"])
    print(json.dumps(data, indent=2))

create_csv()
#json_dump()