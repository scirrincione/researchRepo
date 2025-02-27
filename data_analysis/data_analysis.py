import pandas as pd
import time
import re
import xlsxwriter
import ast

def get_ints_from_string(text):
  return int(re.find(r'\d+', text))

def get_averages():
    data = pd.ExcelFile('../data_collection/tuple_tweet_replies.xlsx')
    av_data = pd.ExcelWriter('replies_averages.xlsx')

    for sheet_name in data.sheet_names:
        sheet = pd.read_excel('../data_collection/tuple_tweet_replies.xlsx', sheet_name)
        comments = 0
        retweets = 0
        quotes = 0
        likes = 0
        reply_vals = {'comment_count': 0, 'retweet_count': 0,'quote_count': 0,'heart_count': 0}
        
        for index,row in sheet.iterrows():
            if index == 1:
                continue
            comments += row['comment_number']
            retweets += row['retweet_number']
            quotes += row['quote_number']
            likes += row['like_number']
            replies = ast.literal_eval(row['replies'])
            for key,value in replies:
                if key in reply_vals:
                    reply_vals[key] += int(value)
                        
        l = len(sheet)
        av_reply_vals = [value/comments for value in reply_vals.values()]
        sheet.loc[l]=([0, 'AVERAGES', '', comments/l, retweets/l, quotes/l, likes/l, str(av_reply_vals)])
        sheet.to_excel(av_data, sheet_name=sheet_name)
    av_data.close()

get_averages()

