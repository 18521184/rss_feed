import feedparser
import requests
import json
import re

from find_feed import findfeed

posts = []

def cleanhtml(raw_html):
#   cleanr = re.compile('<.*?>')
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_posts(rss_url):
    response = feedparser.parse(rss_url)
    for entry in response['entries']:
        if entry['title'] in [x['title'] for x in posts]:
            pass
        else:
            posts.append({
                "title": entry['title'],
                "content":cleanhtml(entry['summary'])
                # "link": each['links'][0]['href'],
                # "tags": [x['term'] for x in each['tags']],
                # "date": time.strftime('%Y-%m-%d', each['published_parsed'])
            })
    return posts

# count = 12

# for x in range(count):
#     if requests.get("{0}/{1}/".format(rss_url, count)).status_code == 200:
#         print("get succeeded, count at: {}".format(count))
#         get_posts_for_ghost("{0}/{1}/".format(rss_url, count))
#         count -= 1
#     else:
#         print("got 404, count at: {}".format(count))
#         count -= 1

url = "https://thanhnien.vn/rss.html"

po_feed = findfeed(url)
a=0
for rss_url in po_feed:
    a+=1
    get_posts(rss_url)
    if a == 10:
        break

for post in posts:
    print(post)
# f = open("bbc_news.json",'w')
# dump = json.dumps(posts)
# f.write(dump)
# f.close()