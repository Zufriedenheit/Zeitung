import feedparser
from datetime import datetime
import pytz
from feedgen.feed import FeedGenerator
import os

now = datetime.now().strftime("%I:%M%p on %B %d, %Y")
rss_feed_urls = [
'https://www.shz.de/lokales/schleswig/rss',
'https://www.shz.de/lokales/gluecksburg-angeln/rss',
'https://www.shz.de/lokales/flensburg/rss',
'https://www.shz.de/deutschland-welt/schleswig-holstein/rss'
]

def get_unique_entries(feeds):
    unique_entries = {}
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            entry_id = entry.get('id') or entry.get('link')
            if entry_id not in unique_entries:
                unique_entries[entry_id] = entry
    return list(unique_entries.values())

def merge_rss_feeds(feed_urls):
    unique_entries = get_unique_entries(feed_urls)
    sorted_entries = sorted(unique_entries, key=lambda entry: entry.published_parsed, reverse=True)
    return sorted_entries




merged_entries = merge_rss_feeds(rss_feed_urls)

fg = FeedGenerator()
fg.title('Lokale Nachrichten')
fg.link(href='https://example.com', rel='alternate')
fg.description('Lokale Nachrichten aus dem Norden')

for entry in merged_entries:
    fe = fg.add_entry()
    fe.id(entry.id)
    fe.title(entry.title)
    fe.link(href=entry.link)
    # fe.description('<![CDATA[' + shzrequests.get_html(entry.link) + ']]>')
    fe.description(entry.summary)
    published_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.timezone('Europe/Berlin'))
    fe.pubDate(published_date)
    fe.enclosure(url=entry.enclosures[0].href, length=entry.enclosures[0].length, type=entry.enclosures[0].type)

# Save the feed to a file
feed_file = os.path.join(os.getcwd(), 'merged_feed.xml')
fg.rss_file(feed_file, pretty=True)

print("Merged RSS feed saved to merged_feed.xml")