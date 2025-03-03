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
        sheet = pd.read_excel(data, sheet_name)
        rep_df = pd.DataFrame(columns = ['comment_count', 'retweet_count', 'quote_count', 'heart_count', 'tweet_body', 'handle'])
        
        for index,row in sheet.iterrows():
            if index == 1:
                continue
           
            replies = ast.literal_eval(row['replies'])
            rep_df = pd.DataFrame(columns = ['comment_count', 'retweet_count', 'quote_count', 'heart_count', 'tweet_body', 'handle'])
            count = 0
            for key,value in replies:
                rep_df.loc[count, key]=value 
                if(key == 'handle'):
                    count+=1
            rep_df.drop_duplicates(subset=['tweet_body'], inplace=True)
            sheet.at[index,'replies'] = rep_df.to_string()
        l = len(sheet)
        av_reply_vals = rep_df.mean(numeric_only=True)
        av_tweet_vals = sheet.mean(numeric_only=True)
        sum_reply_vals = rep_df.sum(numeric_only=True)
        sum_tweet_vals = sheet.sum(numeric_only=True)
        sheet.loc[l]=([0, 'AVERAGES', '', av_tweet_vals['comment_number'], av_tweet_vals['retweet_number'], av_tweet_vals['quote_number'], av_tweet_vals['like_number'], av_reply_vals.to_string()])
        sheet.loc[l+1]=([0, 'SUMS', '', sum_tweet_vals['comment_number'], sum_tweet_vals['retweet_number'], sum_tweet_vals['quote_number'], sum_tweet_vals['like_number'], sum_reply_vals.to_string()])
        sheet.to_excel(av_data, sheet_name=sheet_name)
    av_data.close()

def get_tweet_csv():
    data = pd.ExcelFile('../data_collection/tuple_tweet_replies.xlsx')
    replies = []
    for sheet_name in data.sheet_names:
        sheet = pd.read_excel(data, sheet_name)
        for index, row in sheet.iterrows():
            rep = pd.read_csv(row['replies'])
            
            replies.append(rep['tweet_body'])

    df = pd.DataFrame(replies, columns=['tweet_body'])
    df.to_csv("tweet_replies.csv")


get_tweet_csv()

