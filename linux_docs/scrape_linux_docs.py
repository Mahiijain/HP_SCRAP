import os
import json
import requests
from bs4 import BeautifulSoup

# Set up headers for HTTP requests
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Create a base directory for saving all files
base_dir = "linux_docs"
os.makedirs(base_dir, exist_ok=True)

# Combined data list
all_data = []

# 1. Scrape man7.org
def scrape_man7():
    print("📥 Scraping man7.org...")
    man7_url = "https://man7.org/linux/man-pages/index.html"
    response = requests.get(man7_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select("a[href^='man']")

    for link in links[:5]:  # Limit to top 5 for demo
        href = link.get("href")
        page_url = f"https://man7.org/linux/man-pages/{href}"
        page_resp = requests.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_resp.content, "html.parser")

        title = page_soup.find("h2").get_text(strip=True) if page_soup.find("h2") else "No Title"
        content = page_soup.get_text(separator="\n", strip=True)

        all_data.append({
            "source": "man7.org",
            "title": title,
            "url": page_url,
            "content": content
        })

# 2. Scrape ArchWiki
def scrape_archwiki():
    print("📥 Scraping ArchWiki...")
    archwiki_url = "https://wiki.archlinux.org/title/Table_of_contents"
    response = requests.get(archwiki_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select("div#mw-content-text a[href^='/title/']")

    for link in links[:5]:  # Limit to top 5 for demo
        href = link.get("href")
        page_url = f"https://wiki.archlinux.org{href}"
        page_resp = requests.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_resp.content, "html.parser")

        title = page_soup.find("h1").get_text(strip=True) if page_soup.find("h1") else "No Title"
        content = page_soup.get_text(separator="\n", strip=True)

        all_data.append({
            "source": "archlinux.org",
            "title": title,
            "url": page_url,
            "content": content
        })

# 3. Scrape LinuxHint
def scrape_linuxhint():
    print("📥 Scraping LinuxHint...")
    linuxhint_url = "https://linuxhint.com/"
    response = requests.get(linuxhint_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.select("h2.entry-title a")

    for article in articles[:5]:  # Limit to top 5 for demo
        href = article.get("href")
        page_url = href
        page_resp = requests.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_resp.content, "html.parser")

        title = page_soup.find("h1").get_text(strip=True) if page_soup.find("h1") else "No Title"
        content = page_soup.get_text(separator="\n", strip=True)

        all_data.append({
            "source": "linuxhint.com",
            "title": title,
            "url": page_url,
            "content": content
        })

# Save all collected data into a single JSON file
def save_all_data():
    output_file = os.path.join(base_dir, "all_linux_docs.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print(f"✅ All data saved to: {output_file}")

# Run all scraping functions and save once
scrape_man7()
scrape_archwiki()
scrape_linuxhint()
save_all_data()
