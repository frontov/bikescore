import requests
from bs4 import BeautifulSoup
import json
import re
import hashlib
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def time_to_sec(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2].replace(',', '.')))
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(float(parts[1].replace(',', '.')))
    except Exception:
        pass
    return None

def fetch_race_results(url, page):
    print(f"Scraping race: {url}")
    try:
        page.goto(url, timeout=20000, wait_until="networkidle")
    except Exception as e:
        print(f"  -> Error fetching URL with playwright: {e}")
        return []

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    # Try to find headers to dynamically assign column indexes
    name_idx = -1
    time_idx = -1

    headers = soup.find_all('th')
    if not headers:
        # Sometimes headers are in the first row as td
        first_row = soup.find('tr')
        if first_row:
            headers = first_row.find_all(['td', 'th'])

    for i, th in enumerate(headers):
        text = th.text.lower()
        if "имя" in text or "name" in text or "участник" in text or "спортсмен" in text:
            name_idx = i
        if "время" in text or "time" in text or "результат" in text or "result" in text:
            time_idx = i

    # Fallback to defaults if headers weren't perfectly found
    if name_idx == -1: name_idx = 3 # Typical for timingband
    if time_idx == -1: time_idx = 4

    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > max(name_idx, time_idx):
            name_col = cols[name_idx].text.strip()
            name = name_col.split('\n')[0].strip()

            time_col = cols[time_idx].text.strip()
            time_sec = time_to_sec(time_col)

            if name and time_sec:
                rider_id = "r_" + hashlib.md5(name.encode('utf-8')).hexdigest()[:8]

                # Check for duplicates in current race
                if not any(r['rider_id'] == rider_id for r in results):
                    results.append({
                        "rider_id": rider_id,
                        "rider_name": name,
                        "time_sec": time_sec,
                        "status": "FIN",
                    })
    return results

def scrape_and_load():
    main_url = "https://results.velomarathon.ru/"
    print(f"Fetching main page: {main_url}")
    try:
        response = requests.get(main_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']

        # We look for links pointing out to results/timing sites
        if any(domain in href for domain in ['timingband.ru', 'sportident.online', 'results.zone', 'orgeo.ru', 'vsemsport.ru']):
            title_div = a.find('div', class_='t993__btn-text-title')
            title = title_div.text.strip().lower() if title_div else ""

            if "общий зачет" in title or "общий зачёт" in title:
                continue # Skip overall rankings

            is_kids = "дети" in title or "kids" in title

            links.append((href, is_kids))

    # Deduplicate links
    unique_links = []
    seen_hrefs = set()
    for href, is_kids in links:
        if href not in seen_hrefs:
            unique_links.append((href, is_kids))
            seen_hrefs.add(href)

    print(f"Found {len(unique_links)} race links to parse.")

    base_date = datetime(2024, 1, 1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for idx, (link, is_kids) in enumerate(unique_links):
            results = fetch_race_results(link, page)
            if not results:
                print(f"  -> No valid results found for {link}")
                continue

            print(f"  -> Found {len(results)} valid results. Uploading...")

            category = "mtb"
            if "gravel" in link.lower() or "cx" in link.lower():
                category = "gravel"
            elif "road" in link.lower() or "crit" in link.lower():
                category = "road"

            race_date = (base_date + timedelta(days=idx)).strftime("%Y-%m-%d")

            for res in results:
                res["is_kids"] = is_kids

            payload = {
                "date": race_date,
                "category": category,
                "k_factor": 1.0,
                "results": results
            }

            try:
                api_res = requests.post("http://localhost:8000/api/v1/races", json=payload, timeout=5)
                print(f"  -> API Response: {api_res.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  -> Failed to post data to backend: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_and_load()
