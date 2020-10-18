import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import json
from terminaltables import AsciiTable, SingleTable
import os


def create_shortlink(biglink):
    short_link_api = requests.get(
        'https://api.shrtco.de/v2/shorten', params={'url': biglink})
    short_link_dict = json.loads(short_link_api.text)

    if short_link_dict['ok'] == False:
        return 'error'
    else:
        short_link = short_link_dict['result']['full_short_link']
        return short_link


user_input = input('Enter anything you want to search: ')
modified_input = user_input.replace(' ', '+')

search_param = {'q': modified_input}
r = requests.get('https://google.com/search', params=search_param)

soup = BeautifulSoup(r.text, 'html.parser')

conn = sqlite3.connect('links.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS result(
            biglink text,
            shortlink text)""")

search_title = soup.title.text
search_title = search_title.replace('+', ' ')
data = []
data.append([search_title, 'Link'])


for anchor in soup.find_all('a'):
    biglink = anchor['href']
    headlines = anchor.find_all('h3')
    if len(headlines) != 1 or not biglink.startswith('/url'):
        continue

    biglink = biglink[7:biglink.find('&')]
    headline = headlines[0]

    c.execute("SELECT shortlink FROM result WHERE biglink = (?) LIMIT 1", (biglink,))
    shortlinks = list(map(lambda tup: tup[0], c.fetchall()))


    if len(shortlinks) == 0:
        shortlink = create_shortlink(biglink)
        c.execute("INSERT INTO result VALUES(?,?)", (biglink, shortlink))
        shortlinks.append(shortlink)
    

    if shortlinks[0] != 'error':
        data.append([headline.text, shortlinks[0]])

os.system('cls' if os.name == 'nt' else 'clear')
table_result = SingleTable(data)
table_result.inner_row_border = True
print(table_result.table)

conn.commit()
conn.close()

