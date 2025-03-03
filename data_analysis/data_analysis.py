import pandas as pd
import time
import re
import xlsxwriter
import ast
from io import StringIO

def get_ints_from_string(text):
  return int(re.find(r'\d+', text))

def get_averages():
    data = pd.ExcelFile('../data_collection/tuple_tweet_replies.xlsx')
    av_data = pd.ExcelWriter('replies_averages.xlsx')

    for sheet_name in data.sheet_names:
        sheet = pd.read_excel(data, sheet_name)
        rep_df = pd.DataFrame(columns = ['comment_count', 'retweet_count', 'quote_count', 'heart_count', 'tweet_body', 'handle'])

        for index,row in sheet.iterrows():
            if index == 1:
                continue

            replies = ast.literal_eval(row['replies'])
            this_rep_df = pd.DataFrame(columns = ['comment_count', 'retweet_count', 'quote_count', 'heart_count', 'tweet_body', 'handle'])
            count = 0
            for key,value in replies:
                this_rep_df.loc[count, key]=value
                if(key == 'handle'):
                    count+=1
            this_rep_df.drop_duplicates(subset=['tweet_body'], inplace=True)
            sheet.at[index,'replies'] = str(this_rep_df.to_dict())
            rep_df = pd.concat([rep_df, this_rep_df], ignore_index=True)

        l = len(sheet)

        av_reply_vals = rep_df[['comment_count', 'retweet_count', 'quote_count', 'heart_count']].astype(int).mean()
        av_tweet_vals = sheet.mean(numeric_only=True)
        sum_reply_vals = rep_df[['comment_count', 'retweet_count', 'quote_count', 'heart_count']].astype(int).sum()
        sum_tweet_vals = sheet.sum(numeric_only=True)

        sheet.loc[l]=([0, 'AVERAGES', '', av_tweet_vals['comment_number'], av_tweet_vals['retweet_number'], av_tweet_vals['quote_number'], av_tweet_vals['like_number'], str(av_reply_vals.to_list())])
        sheet.loc[l+1]=([0, 'SUMS', '', sum_tweet_vals['comment_number'], sum_tweet_vals['retweet_number'], sum_tweet_vals['quote_number'], sum_tweet_vals['like_number'], str(sum_reply_vals.to_list())])
        sheet.to_excel(av_data, sheet_name=sheet_name)
    av_data.close()

def get_tweet_csv():
    data = pd.ExcelFile('../data_collection/tuple_tweet_replies.xlsx')
    replies = []
    for sheet_name in data.sheet_names:
        sheet = pd.read_excel(data, sheet_name)
        for index, row in sheet.iterrows():
            rep = ast.literal_eval(row['replies'])
            for key, value in rep:
                if key == 'tweet_body':
                    replies.append(value)

    df = pd.DataFrame(replies, columns=['tweet_body'])
    df.drop_duplicates(subset=['tweet_body'], inplace=True)
    df.to_csv("tweet_replies_from_tuple.csv")


get_tweet_csv()

