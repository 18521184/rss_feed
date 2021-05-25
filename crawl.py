import re, json, feedparser

import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

from preprocessing import is_relevant, cleanhtml, find_feeds, normalize

# 
def get_content(url):
    # Crawl and parse meta data of the article from server
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(url)

    soup = BeautifulSoup(page, "lxml")
    content = ''

    try:
        if 'tuoitre.vn' in url:
            # We get the first element in the array because we are sure that 
            # any article on tuoitre.vn only has one div tag with classname "main-content-body"
            # Note that findAll or find_all always return a list 
            raw = soup.findAll("div", {"class": "main-content-body"})[0]


            # Nonetheless, raw main content body still have some noise
            # such as div tag used for images or suggesting a related article.
            # Thus, we need to get rid of those by extracting p tag only
            # because p tag contains merely paragraph of the content that we need.
            content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": None, "style": None})])

        elif 'vnexpress' in url:
            raw = soup.find_all('article', attrs={"class": "fck_detail"})[0]
            paras = raw.find_all('p', attrs={'class': "Normal", 'style': None, 'id': None})

            content = normalize(' '.join([cleanhtml(str(p)) for p in paras]))

        elif 'thanhnien.vn' in url:
            raw = soup.findAll("div", {"id": "abody"})[0]
            divs = raw.findAll("div", attrs={"class": None, "id": None, "style": None})
                
            new_divs = []
            for div in divs:
                s = str(div)
                if '<table ' not in s and 'Ảnh: ' not in s:
                    new_divs.append(cleanhtml(s))

            content = ''.join(new_divs)

        elif 'nld.com.vn' in url:
            pass
        elif 'vietnamnet.vn' in url:
            pass
    except Exception as err:
        print('Error at:',url)
        print('Error details:', err)
        return content

    content = normalize(content)

    return content

def crawl():
    # # Aggregate all RSS feeds URL from RSS aggregator site
    # rss_aggr_urls = [
    #     'https://tuoitre.vn/rss.htm',
    #     'https://vnexpress.net/rss',
    #     'https://thanhnien.vn/rss.html',
    #     'http://vietnamnet.vn/vn/rss/',
    #     'https://nld.com.vn/rss.htm'
    # ]
    rss_aggr_urls = [
        'https://tuoitre.vn/rss.htm'
    ]
    # List of sites to be ignored due to not containing usable information
    blacklist = [
        'thanhnien.vn/video/',
    ]

    for site in rss_aggr_urls:
        feeds_url = find_feeds(site)

        return_data = {
            "site": site,
            "feeds": []
        }
        data = None

        for url in feeds_url:
            # Check if the url is in blacklist
            if url in blacklist:
                continue

            data = {
                "rss_url": url,
                "articles": []
            }

            # Test with particular RSS feed
            feed = feedparser.parse(url)

            for i in range(len(feed.entries)):
                # Get a sample article URL
                # Also its title
                url = feed.entries[i].links[0]['href']
                title = feed.entries[i].title
                summary = cleanhtml(feed.entries[i].summary)  

                content = get_content(url)

                # Check if the content is attainable
                # Also check if the article is relevant to COVID-19
                # If we use summary and title, it would be faster and less resource consumption
                # Nonetheless, the summary is not very reliable.
                if len(content) != 0 and is_relevant(title)==False and is_relevant(content)==False:
                    # If none match, continue to another aritcle
                    continue

                # # Get content's header (somehow as similar as summary)
                # # Note that we can convert bs4.element.XXX to string by str() or call .string attribute
                # # summary field is also content header
                # content_header = cleanhtml(str(raw_content.findAll("h2", {"class": "sapo"})[0]))

                data['articles'].append({
                    "id": feed.entries[i].id,
                    "summary": summary,
                    "title": title,
                    "content": content,
                    "url": url,
                    "publish_date": feed.entries[i].published
                })

            if len(data.articles) > 0:
                return_data['feeds'].append(data)
    
    return return_data

def get_data():
    data = []
    data.append(crawl())

    f = open('crawl_central.txt', 'w+')
    f.write(json.dumps(data, indent=4, ensure_ascii=False))
    f.close()

    print(len(data[0]['feeds'])*len(data[0]['feeds'][0]['articles']))
    
get_data()


# Key extracting
## source
# // feed.feed.docs for overall
# // feed.entries[idx].link(s) for detail
# // feed.entries[idx].title_detail.base for RSS source hyperlink
## date // feed.feed.published
## unicity // feed.entries[0].id
## Can I get more than 30 article per RSS feed request? (Can not)
## How do I get all RSS feed via an RSS aggregator site? (find_feed)

# Stucture of the JSON dataset
# [{
#     "site": "",
#     "feeds": [
#         {
#             "rss_url": "",
#             "articles": [{
#                 "id": "",
#                 "summary": "",
#                 "title": "",
#                 "content": "",
#                 "url": "",
#                 "publish_date": "",
#             }]
#         }
#     ]
# }]
 