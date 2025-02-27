import requests as req
from bs4 import BeautifulSoup


dep_reddit = req.get('https://www.reddit.com/r/depression/')

print(dep_reddit)

soup = BeautifulSoup(dep_reddit.content, 'html.parser')

s = soup.find('div', class_='entry-content')

lines = soup.find_all('p')

for line in lines: 
    print(line.text)
    print(line.type)