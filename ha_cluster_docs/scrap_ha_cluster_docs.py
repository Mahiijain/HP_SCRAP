import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

# List of High Availability (HA) URLs to crawl
URLS = [
    "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/configuring_and_managing_high_availability_clusters/assembly_overview-of-high-availability-configuring-and-managing-high-availability-clusters",
    "https://learn.microsoft.com/en-us/azure/sap/workloads/high-availability-guide-rhel-pacemaker?tabs=msi",
    "https://documentation.suse.com/sle-ha/15-SP6/html/SLE-HA-all/article-installation.html",
    "https://documentation.suse.com/sle-ha/15-SP6/html/SLE-HA-all/book-administration.html",
    "https://docs.aws.amazon.com/sap/latest/sap-hana/sap-hana-on-aws-ha-cluster-configuration-on-sles.html",
    "http://nakivo.com/blog/vmware-cluster-ha-configuration/",
    "https://www.netapp.com/blog/cvo-blg-high-availability-cluster-concepts-and-architecture/",
    "https://pve.proxmox.com/wiki/High_Availability",
    "https://clusterlabs.org/projects/pacemaker/doc/deprecated/",
    "https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/#s-ha-pacemaker"
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

    with open("ha_cluster_documentation.json", "w", encoding="utf-8") as json_file:
        json.dump(all_documentation_data, json_file, ensure_ascii=False, indent=2)

    print("\nDone. Data saved to 'ha_cluster_documentation.json'.")
