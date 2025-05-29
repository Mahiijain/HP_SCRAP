import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

# List of IP address-related documentation URLs
URLS = [
    "https://phoenixnap.com/kb/linux-ip-command-examples",
    "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/networking_guide/sec-configuring_ip_networking_with_ip_commands#sec-Configuring_IP_Networking_with_ip_Commands",
    "https://www.juniper.net/documentation/us/en/software/junos/interfaces-security-devices/topics/topic-map/security-interface-ipv4-ipv6-protocol.html"
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

def crawl_and_extract(url):
    results = []

    print(f"\nFetching main page: {url}")
    main_text = extract_text_from_url(url)
    if main_text:
        results.append({"url": url, "content": main_text})

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to re-fetch {url} for link parsing: {e}")
        return results

    soup = BeautifulSoup(response.content, "html.parser")

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if is_valid_link(href):
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == urlparse(url).netloc:
                page_text = extract_text_from_url(full_url)
                if page_text:
                    results.append({"url": full_url, "content": page_text})
                    time.sleep(0.5)  # polite crawling

    return results

if __name__ == "__main__":
    all_data = []

    for link in URLS:
        site_data = crawl_and_extract(link)
        all_data.extend(site_data)

    with open("ip_documentation.json", "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=2)

    print("\nDone. Data saved to 'ip_documentation.json'.")
