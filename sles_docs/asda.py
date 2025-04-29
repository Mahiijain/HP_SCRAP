import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

# Base documentation URL
BASE_URL = "https://documentation.suse.com/sles/15-SP4/html/SLES-all/book-administration.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

visited = set()

def is_valid_link(href):
    return href and not href.startswith('#') and not href.startswith('mailto:')

def extract_text_from_url(url):
    if url in visited:
        return None
    visited.add(url)

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.get_text(separator='\n', strip=True)
    print(f"Extracted content from: {url}")
    return content

def crawl_and_extract(base_url):
    results = []

    # Get main page content
    print("Fetching main page...")
    main_text = extract_text_from_url(base_url)
    if main_text:
        results.append({"url": base_url, "content": main_text})

    # Parse links from main page
    print("Parsing links...")
    response = requests.get(base_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if is_valid_link(href):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                page_text = extract_text_from_url(full_url)
                if page_text:
                    results.append({"url": full_url, "content": page_text})
                    time.sleep(0.5)  # polite crawling

    return results

if __name__ == "__main__":
    documentation_data = crawl_and_extract(BASE_URL)

    with open("suse_documentation.json", "w", encoding="utf-8") as json_file:
        json.dump(documentation_data, json_file, ensure_ascii=False, indent=2)

    print("Done. Data saved to 'suse_documentation.json'.")
