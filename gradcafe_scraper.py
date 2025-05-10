# Save this in ./scrapers/gradcafe_scraper.py (NOT a notebook cell)
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_page(url, output_dir, page_num):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        os.makedirs(output_dir, exist_ok=True)
        with open(f"{output_dir}/page_{page_num}.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        return soup
    else:
        print(f"Failed to fetch {url}: Status {response.status_code}")
        return None

def scrape_site(base_url, num_pages, output_dir):
    data = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}&p={page}"  # GradCafe-specific URL pattern
        print(f"Scraping {url}")
        soup = fetch_page(url, output_dir, page)
        if soup:
            # Placeholder for parsing (to be customized in Step 3)
            posts = soup.find_all("tr", class_="row")  # GradCafe table rows
            for post in posts:
                entry = parse_post(post)
                if entry:
                    data.append(entry)
        time.sleep(random.uniform(2, 5))  # Polite delay
    return data

def parse_post(post):
    try:
        univ_name = post.find("td", class_="tcol1").text.strip() if post.find("td", class_="tcol1") else "Unknown"
        cgpa = extract_score(post, "gpa")
        gre_v = extract_score(post, "gre.*v.*?(\\d+)")
        gre_q = extract_score(post, "gre.*q.*?(\\d+)")
        gre_a = extract_score(post, "gre.*w.*?(\\d+\\.\\d+)")
        decision = post.find("td", class_="tcol3").text.strip() if post.find("td", class_="tcol3") else None
        if cgpa and gre_v and gre_q and gre_a and decision == "Accepted":
            return {"univName": univ_name, "cgpa": cgpa, "greV": gre_v, "greQ": gre_q, "greA": gre_a, "decision": decision}
        return None
    except Exception as e:
        print(f"Error parsing post: {e}")
        return None

def extract_score(post, pattern):
    import re
    text = post.text.lower()
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None

if __name__ == "__main__":
    base_url = "https://thegradcafe.com/survey/index.php?q=u%2A&t=a&pp=250&o=d"
    num_pages = 5
    output_dir = "./data/raw_html/gradcafe"
    scraped_data = scrape_site(base_url, num_pages, output_dir)
    df = pd.DataFrame(scraped_data)
    df.to_csv("./data/csv/gradcafe_data.csv", index=False)
    print(f"Saved {len(df)} entries to gradcafe_data.csv")