import re
import datetime
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Fetch the FT Syria page HTML
url = "https://www.ft.com/syria"
headers = {"User-Agent": "Mozilla/5.0"}  # simulate a browser user agent
response = requests.get(url, headers=headers)
response.raise_for_status()  # ensure we got a 200 OK response
html = response.text

# Parse the page with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Prepare the RSS root and channel elements
ET.register_namespace('media', 'http://search.yahoo.com/mrss/')  # Media RSS namespace for media:content
rss = ET.Element('rss', {"version": "2.0"})
rss.set('xmlns:media', "http://search.yahoo.com/mrss/")
channel = ET.SubElement(rss, 'channel')
# Channel metadata
ET.SubElement(channel, 'title').text = "FT.com Syria News"
ET.SubElement(channel, 'link').text = "https://www.ft.com/syria"
ET.SubElement(channel, 'description').text = "Latest news on Syria from the Financial Times"
# Use current time as channel lastBuildDate
now = datetime.datetime.utcnow()
ET.SubElement(channel, 'lastBuildDate').text = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

# Find the list of news items on the page
# The page groups articles by date headings (e.g., "Wednesday, 30 April, 2025").
# We'll iterate through list elements in order, tracking the current date.
current_pubdate = None
news_list = soup.find('ul')  # find the first <ul> (assuming the listing is the main list)
if news_list:
    for li in news_list.find_all('li', recursive=False):
        # If this list item has no anchor, it might be a date header
        if li.find('a') is None:
            # Check if text looks like a date (Day, DD Month, YYYY)
            date_text = li.get_text(strip=True)
            if re.match(r'^[A-Za-z]+, \d+ \w+, \d{4}$', date_text):
                # Parse and format this date for pubDate
                try:
                    dt = datetime.datetime.strptime(date_text, "%A, %d %B, %Y")
                    # Use 00:00:00 GMT for pubDate time (no time provided on page)
                    current_pubdate = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
                except ValueError:
                    current_pubdate = None
            continue  # move to next list item
        # Otherwise, this li contains an article entry
        # Find the main article link (href contains '/content/')
        link_tag = li.find('a', href=lambda h: h and '/content/' in h)
        if not link_tag:
            continue
        article_url = link_tag.get('href')
        if article_url.startswith('/'):
            article_url = "https://www.ft.com" + article_url  # make absolute URL
        title_text = link_tag.get_text(strip=True)

        # The snippet/description might be in a second <a> with the same href
        desc_text = ""
        link_tags = li.find_all('a', href=lambda h: h and '/content/' in h)
        if len(link_tags) > 1:
            desc_text = link_tags[1].get_text(strip=True)
        else:
            desc_text = ""  # if no separate snippet, leave description empty or use title

        # Find image URL for media:content if present
        media_url = None
        img_tag = li.find('a', href=lambda h: h and 'cloudfront.net' in h)
        if img_tag:
            img_href = img_tag.get('href')
            # Decode the image URL if it's embedded in the origami service URL
            match = re.search(r'raw/(https%3A%2F%2F[^?]+)', img_href)
            if match:
                media_url = requests.utils.unquote(match.group(1))
            elif img_href.startswith('http'):
                media_url = img_href

        # Use the last seen date header for pubDate (if none, use current time as fallback)
        pub_date = current_pubdate or now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Build RSS item element
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = title_text
        ET.SubElement(item, 'link').text = article_url
        ET.SubElement(item, 'description').text = desc_text
        ET.SubElement(item, 'pubDate').text = pub_date
        if media_url:
            ET.SubElement(item, 'media:content', {
                "url": media_url,
                "type": "image/jpeg"
            })

# Write the RSS XML to file
tree = ET.ElementTree(rss)
tree.write('syria_fixed.xml', encoding='utf-8', xml_declaration=True)
