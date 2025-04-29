import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

# List of URLs to crawl
URLS = [
    "http://www.ntp.org/",
    "https://ubuntu.com/server/docs/network-ntp",
    "https://documentation.suse.com/sles/15-SP4/html/SLES-all/cha-ntp.html",
    "https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_basic_system_settings/using-ntp-to-synchronize-time_basic-system-configuration",
    "https://www.ntppool.org/zone/@",
    "https://tf.nist.gov/tf-cgi/servers.cgi",
    "https://www.ntp-servers.net/",
    "https://support.ntp.org/bin/view/Servers/NTPPoolServers",
    "http://www.eecis.udel.edu/~mills/ntp/clock.html"
]

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
        response = requests.get(url, headers=HEADERS, timeout=10)
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
    print(f"\nFetching main page: {base_url}")
    main_text = extract_text_from_url(base_url)
    if main_text:
        results.append({"url": base_url, "content": main_text})

    # Parse links from main page
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to re-fetch {base_url} for link parsing: {e}")
        return results

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
    all_documentation_data = []

    for url in URLS:
        documentation_data = crawl_and_extract(url)
        all_documentation_data.extend(documentation_data)

    with open("ntp_documentation.json", "w", encoding="utf-8") as json_file:
        json.dump(all_documentation_data, json_file, ensure_ascii=False, indent=2)

    print("\nDone. Data saved to 'ntp_documentation.json'.")
