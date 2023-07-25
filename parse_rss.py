import feedparser
from datetime import datetime
import pytz
from feedgen.feed import FeedGenerator
import os
from bs4 import BeautifulSoup
import requests
import minify_html

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

def remove_elements(soup, elements_to_remove):
    for element in elements_to_remove:
        for tag in soup.find_all(element):
            tag.decompose()

def get_clean_version(url):
    # output_file = "/Users/Joshua/Developer/RSS/output.html"
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Find the start and end positions of the comments
    start_comment = "<!-- start content-stage -->"
    end_comment = "<!-- start social bar -->"
    start_pos = html_content.find(start_comment)
    end_pos = html_content.find(end_comment)

    # Extract the middle part between the comments
    middle_part = html_content[start_pos + len(start_comment):end_pos].strip()

    # Parse the middle part using BeautifulSoup
    soup = BeautifulSoup(middle_part, "html.parser")

    # Elements to remove
    elements_to_remove = ['svg', 'button', 'input', 'script']
    remove_elements(soup, elements_to_remove)

    # Remove all divs with the class "related-content"
    for div in soup.find_all('div', class_='related-content'):
        div.decompose()
    # Minify html
    minified_html = minify_html.minify(str(soup))
    return minified_html


# URLs to request feeds from
rss_feed_urls = [
'https://www.shz.de/lokales/schleswig/rss',
'https://www.shz.de/lokales/gluecksburg-angeln/rss',
'https://www.shz.de/lokales/flensburg/rss',
'https://www.shz.de/deutschland-welt/schleswig-holstein/rss'
]

# Get List of IDs already inside the merged feed file
now = datetime.now().strftime("%I:%M%p on %B %d, %Y")
feed_file = os.path.join(os.getcwd(), 'merged_feed.xml')
with open(feed_file) as file:
    merge_feed_string = file.read()

already_inside_ids = []
existing_feed = feedparser.parse(merge_feed_string)
for entry in existing_feed.entries:
    already_inside_ids.append(entry.get('id'))

# Get list of entries that are not already inside feed file and no dublicats from feed urls
def get_unique_entries(feeds):
    unique_entries = {}
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            entry_id = entry.get('id')
            if entry_id not in already_inside_ids:
                if entry_id not in unique_entries:
                    unique_entries[entry_id] = entry
    return list(unique_entries.values())

# Get sorted list of entries to append to file
def merge_rss_feeds(feed_urls):
    unique_entries = get_unique_entries(feed_urls)
    sorted_entries = sorted(unique_entries, key=lambda entry: entry.published_parsed, reverse=True)
    return sorted_entries



merged_entries = merge_rss_feeds(rss_feed_urls)

fg = FeedGenerator()
fg.id('www.shz.de')
fg.title('Lokale Nachrichten')
fg.link(href='https://shz.de', rel='alternate')
fg.description('Lokale Nachrichten aus dem Norden')

# Add existing entries
for entry in existing_feed.entries:
    fe = fg.add_entry()
    fe.id(entry.id)
    fe.title(entry.title)
    fe.link(href=entry.link)
    fe.content(entry.content[0].value)
    published_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.timezone('Europe/Berlin'))
    fe.pubDate(published_date)

# Add new entries
for entry in merged_entries:
    fe = fg.add_entry()
    fe.id(entry.id)
    fe.title(entry.title)
    fe.link(href=entry.link)
    fe.content(content=get_clean_version(entry.link), type="html")
    published_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.timezone('Europe/Berlin'))
    fe.pubDate(published_date)

# Save the feed to a file
fg.atom_file(feed_file, pretty=True)
