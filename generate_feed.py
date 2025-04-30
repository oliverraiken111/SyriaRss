import requests
from bs4 import BeautifulSoup
import datetime
import xml.etree.ElementTree as ET

# FT Syria section
url = "https://www.ft.com/syria"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Set up RSS feed
ET.register_namespace('media', 'http://search.yahoo.com/mrss/')
rss = ET.Element('rss', {"version": "2.0", "xmlns:media": "http://search.yahoo.com/mrss/"})
channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = "FT.com Syria News"
ET.SubElement(channel, 'link').text = url
ET.SubElement(channel, 'description').text = "Latest news on Syria from the Financial Times"
ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

# Extract Syria-specific articles
articles_found = 0
seen_titles = set()

# FT article containers typically use a tag like 'a' inside a div with class="o-teaser__heading"
for teaser in soup.select('a.js-teaser-heading-link[href^="/content/"]'):
    title = teaser.get_text(strip=True)
    href = teaser["href"]

    if not title or title in seen_titles:
        continue

    seen_titles.add(title)
    full_url = "https://www.ft.com" + href

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = full_url
    ET.SubElement(item, "description").text = f"FT article on Syria: {title}"
    ET.SubElement(item, "pubDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    articles_found += 1
    if articles_found >= 10:
        break

# Write output
with open("syria_fixed.xml", "wb") as f:
    ET.ElementTree(rss).write(f, encoding="utf-8", xml_declaration=True)

print(f"✅ RSS feed created with {articles_found} Syria-specific articles.")
