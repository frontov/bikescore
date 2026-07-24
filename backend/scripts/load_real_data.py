import requests
from bs4 import BeautifulSoup
import json
import re
import hashlib
from datetime import datetime, timedelta

def time_to_sec(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        pass
    return None

def fetch_race_results(url):
    print(f"Scraping race: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  -> Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    results = []

    # Look for generic table rows
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            name_col = cols[3].text.strip()
            name = name_col.split('\n')[0].strip()

            time_col = cols[4].text.strip()
            time_sec = time_to_sec(time_col)

            if name and time_sec:
                rider_id = "r_" + hashlib.md5(name.encode('utf-8')).hexdigest()[:8]

                # Check for duplicates in current race
                if not any(r['rider_id'] == rider_id for r in results):
                    results.append({
                        "rider_id": rider_id,
                        "rider_name": name,
                        "time_sec": time_sec,
                        "status": "FIN"
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

    # Find all links on the main page that point to timingband.ru
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'timingband.ru/results/' in href:
            links.append(href)

    # Deduplicate links
    links = list(set(links))
    print(f"Found {len(links)} race links to parse.")

    base_date = datetime(2024, 1, 1)
    for idx, link in enumerate(links):
        results = fetch_race_results(link)
        if not results:
            print(f"  -> No valid results found for {link}")
            continue

        print(f"  -> Found {len(results)} valid results. Uploading...")

        # Determine category based on link text or URL (fallback to mtb)
        category = "mtb"
        if "gravel" in link.lower() or "cx" in link.lower():
            category = "gravel"
        elif "road" in link.lower() or "crit" in link.lower():
            category = "road"

        race_date = (base_date + timedelta(days=idx)).strftime("%Y-%m-%d")

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

if __name__ == "__main__":
    scrape_and_load()
