import requests
from bs4 import BeautifulSoup
import datetime
import xml.etree.ElementTree as ET

# Target FT Syria page
url = "https://www.ft.com/syria"
headers = {"User-Agent": "Mozilla/5.0"}

# Fetch and parse
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Set up RSS structure
ET.register_namespace('media', 'http://search.yahoo.com/mrss/')
rss = ET.Element('rss', {"version": "2.0", "xmlns:media": "http://search.yahoo.com/mrss/"})
channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = "FT.com Syria News"
ET.SubElement(channel, 'link').text = url
ET.SubElement(channel, 'description').text = "Latest news on Syria from the Financial Times"
ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

# Target the list of Syria articles specifically
seen_urls = set()
articles_found = 0

# Find <ul> that likely contains the Syria news list
main_list = soup.find("ul")
if not main_list:
    print("❌ Could not find the Syria article list.")
else:
    for li in main_list.find_all("li", recursive=False):
        a_tag = li.find("a", href=True)
        if not a_tag:
            continue

        href = a_tag["href"]
        title = a_tag.get_text(strip=True)

        if not href.startswith("/content/") or not title or title in seen_urls:
            continue

        full_url = "https://www.ft.com/syria" + href
        seen_urls.add(title)

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = full_url
        ET.SubElement(item, "description").text = f"FT article on Syria: {title}"
        ET.SubElement(item, "pubDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        articles_found += 1
        if articles_found >= 10:
            break

# Write to XML (in binary mode to avoid encoding error)
with open("syria_fixed.xml", "wb") as f:
    ET.ElementTree(rss).write(f, encoding="utf-8", xml_declaration=True)

print(f"✅ RSS feed created with {articles_found} Syria-specific articles.")
