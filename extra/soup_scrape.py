import requests
from bs4 import BeautifulSoup
import csv

username = "jarvis"
URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
r = requests.get(URL)
 
soup = BeautifulSoup(r.content, 'html5lib')
 
tweets=[]  # a list to store quotes
 
print(soup.prettify())