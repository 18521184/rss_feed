import feedparser
rss_document = """
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>Sample Feed</title>
<description>For documentation &lt;em&gt;only&lt;/em&gt;</description>
<link>http://example.org/</link>
<pubDate>Sat, 07 Sep 2002 00:00:01 GMT</pubDate>
<!-- other elements omitted from this example -->
<item>
<title>First entry title</title>
<link>http://example.org/entry/3</link>
<description>Watch out for &lt;span style="background-image:
url(javascript:window.location='http://example.org/')"&gt;nasty
tricks&lt;/span&gt;</description>
<pubDate>Thu, 05 Sep 2002 00:00:01 GMT</pubDate>
<guid>http://example.org/entry/3</guid>
<!-- other elements omitted from this example -->
</item>
</channel>
</rss>
"""
rss = feedparser.parse(rss_document)

# Channel Details

print ("-----Channel Details-----")

print (rss.feed.title)
print (rss.feed.description)
print (rss.feed.link)

# Item Details

print ("-----Item Details-----")
for fee in rss.entries:
    print (fee.title)
    print (fee.summary)
    print (fee.link)