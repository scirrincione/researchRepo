from playwright.sync_api import sync_playwright
import csv
import os


def scrape_tweet(url: str) -> dict:
    """
    Scrape a single tweet page for Tweet thread e.g.:
    https://twitter.com/Scrapfly_dev/status/1667013143904567296
    Return parent tweet, reply tweets and recommended tweets
    """
    _xhr_calls = []
    
    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # enable background request intercepting:
        page.on("response", intercept_response)
        # go to url and wait for the page to load
        page.goto(url)
        page.wait_for_selector("[class='tweet-content media-body']")
        '''
        
        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(1000)
        #'testid'="logged_out_read_replies_pivot"
        page.locator("[data-testid='logged_out_read_replies_pivot']").click()
        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(1000)
        
        tweets = []
        while True:
            prev_tweet_count = len(tweets)
            for i in range(2):
                page.mouse.wheel(0, 15000)
                page.wait_for_timeout(1000)
                new_tweets = page.query_selector_all("[data-testid='tweet']")
                for tweet in new_tweets[len(tweets):]:
                    html = tweet.inner_html()
                    tweets.append(html)
                    if len(tweets) == prev_tweet_count:
                        break
        
        print(tweets[0])'''
        
        # find all tweet background requests:
        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        print(_xhr_calls)
        for xhr in tweet_calls:
            
            data = xhr.json()
            recursiveField(data, "")
            return data['data']['tweetResult']['result']


def recursiveField(data, indent):
    print("recursion start")
    for field in data:
        print(indent,field)
        if type(data[field]) == dict:
            recursiveField(data[field], "  " + indent)
        else:
            print(indent,"Value: ", data[field])


def makeCSV(data):
    print("Making CSV")
    with open("tweets.csv", "w", newline = "") as pf:
        writer = csv.writer(pf)
        writer.writerow(["Username", "Tweet", "Date", "Replies", "Retweets", "Likes"])
        with open('usernames.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                username = line.strip()
                print("Username: ", username)

if __name__ == "__main__":
    tweet_json = scrape_tweet("https://nitter.net/jarvis/status/1886523096506753500#m")
    #recursiveField(tweet_json)
#dict_keys(['__typename', 'rest_id', 'core', 'unmention_data', 'edit_control', 'is_translatable', 'views', 'source', 'grok_analysis_button', 'quoted_status_result', 'legacy'])
#tweet is under legacy