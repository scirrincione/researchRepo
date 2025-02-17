import matplotlib.pyplot as plt 
import pandas as pd
from datetime import datetime
import string


#sources: pandas documentation, python documentation, geek for geeks, claude, stack overflow, kaggle

# Convert data to dataframe
dep_frame = pd.read_csv("depression-sampled.csv", sep = ",", header = 0)

# total number of posts
print("The total number of posts is: ", len(dep_frame))

# number of unique authors
print("Number of unique authors: ", len(pd.unique(dep_frame["author"])))

# average post length
# split post content column into list using " " as separator
content_column = dep_frame["selftext"].dropna().str.split(expand = False, regex = False)
post_lens = [len(x) for x in content_column]
print("The average post length: ", pd.Series(post_lens).mean())

# date range 
# When grabbing the UTC column for some reason reddit links were being grabbed as well so I removed any non-numeric entries from the column
min = datetime.fromtimestamp(pd.to_numeric(dep_frame["created_utc"][pd.to_numeric(dep_frame["created_utc"], errors='coerce').notnull()]).min())
max = datetime.fromtimestamp(pd.to_numeric(dep_frame["created_utc"][pd.to_numeric(dep_frame["created_utc"], errors='coerce').notnull()]).max())
print("The date range of the dataset is ", min, " to ", max)

# Most common words with Claude
# Stripping all punctuation and making all the words lowercase for comparison
common_words = content_column.explode().str.lower().str.strip(string.punctuation)
stop_words = pd.read_csv("stop-words.txt", header = 0)
common_words_dropped = common_words[~common_words.isin(stop_words["word"])]

word_counts = common_words_dropped.value_counts()
unedited_word_counts = common_words.value_counts()
print("Most common words")
print(unedited_word_counts[1:20])
print("Most common words dropping list of stop words made with Claude")
print(word_counts[1:20])

# Temporal graph