import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import json

from parser.parsers.factory import get_parser
from parser.models import RacePayload

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
            parser_instance = get_parser(link)
            results = parser_instance.parse(link, page)

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
                res.is_kids = is_kids

            payload = RacePayload(
                date=race_date,
                category=category,
                k_factor=1.0,
                results=results
            )

            try:
                # Convert the pydantic model to a dict, which handles serialization of objects correctly
                payload_dict = payload.model_dump()
                api_res = requests.post("http://localhost:8000/api/v1/races", json=payload_dict, timeout=5)
                print(f"  -> API Response: {api_res.status_code}")
                if api_res.status_code != 200:
                    print(f"  -> API Error Detail: {api_res.text}")
            except requests.exceptions.RequestException as e:
                print(f"  -> Failed to post data to backend: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_and_load()
