import requests
from bs4 import BeautifulSoup
import datetime
import xml.etree.ElementTree as ET

# Setup
url = "https://www.ft.com/syria"
headers = {"User-Agent": "Mozilla/5.0"}

# Fetch the page
response = requests.get(url, headers=headers)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html, "html.parser")

# Create the RSS feed structure
ET.register_namespace('media', 'http://search.yahoo.com/mrss/')
rss = ET.Element('rss', {"version": "2.0", "xmlns:media": "http://search.yahoo.com/mrss/"})
channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = "FT.com Syria News"
ET.SubElement(channel, 'link').text = "https://www.ft.com/syria"
ET.SubElement(channel, 'description').text = "Latest news on Syria from the Financial Times"
ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

# Extract articles
seen_urls = set()
articles_found = 0

for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    if '/content/' in href and href not in seen_urls:
        full_url = "https://www.ft.com" + href if href.startswith("/") else href
        title = a_tag.get_text(strip=True)

        if len(title) < 10:
            continue

        seen_urls.add(href)

        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'link').text = full_url
        ET.SubElement(item, 'description').text = f"FT article on Syria: {title}"
        ET.SubElement(item, 'pubDate').text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        articles_found += 1
        if articles_found >= 10:
            break

# Write RSS feed to file (corrected binary write mode)
with open("syria_fixed.xml", "wb") as f:
    ET.ElementTree(rss).write(f, encoding="utf-8", xml_declaration=True)

print(f"✅ RSS feed created with {articles_found} articles.")
