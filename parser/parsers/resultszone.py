import hashlib
import re
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from parser.parsers.base import BaseParser
from parser.models import Result

class ResultsZoneParser(BaseParser):
    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        return 'results.zone' in url.lower()

    def parse(self, url: str, page: Page) -> List[Result]:
        print(f"ResultsZoneParser: Scraping event {url}")
        try:
            page.goto(url, timeout=20000, wait_until="networkidle")
        except Exception as e:
            print(f"  -> Error fetching URL with playwright: {e}")
            return []

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # results.zone often has sub-races on the main event page.
        # Links to these results look like: /5moscow-velomarathon-2025/races/8233/results
        # Let's see if we are on the main event page or a specific race page
        if "/races/" not in url:
            race_links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/races/" in href and "/results" in href:
                    full_link = f"https://results.zone{href}" if href.startswith('/') else href
                    race_links.add(full_link)

            print(f"  -> Found {len(race_links)} sub-race links on the event page.")
            all_results = []
            for sub_link in race_links:
                all_results.extend(self._parse_race_page(sub_link, page))

            # Deduplicate by rider_id across the whole event if necessary, or just return
            deduped = {}
            for r in all_results:
                if r.rider_id not in deduped:
                    deduped[r.rider_id] = r
            return list(deduped.values())
        else:
            return self._parse_race_page(url, page)

    def _parse_race_page(self, url: str, page: Page) -> List[Result]:
        print(f"  -> Parsing specific race: {url}")
        try:
            page.goto(url, timeout=20000, wait_until="networkidle")
            # results.zone loads data asynchronously sometimes, so let's wait a bit for the table
            page.wait_for_selector("table.b-table", timeout=10000)
        except Exception as e:
            print(f"  -> Error or timeout waiting for table on {url}: {e}")
            pass # Try to parse whatever is there anyway

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        table = soup.find('table', class_='b-table')
        if not table:
            return []

        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')

        for row in rows:
            # find name
            name_tag = row.find('a', class_='participant-summary__name')
            if not name_tag:
                continue
            name = name_tag.text.strip()

            # find time
            # results.zone typically puts time in the last column or one with `font-weight-bold`
            time_sec = None
            cols = row.find_all('td')
            for col in reversed(cols):
                text = col.text.strip()
                # matches 00:51:44.21 or 00:51:44
                if re.match(r'^\d{2}:\d{2}:\d{2}', text) or re.match(r'^\d{1,2}:\d{2}:\d{2}', text):
                    # We might have invisible span inside, so let's try to get clean text
                    clean_text = text.split('\n')[0].strip()
                    # take just the HH:MM:SS part for time_to_sec, ignoring milliseconds
                    time_part = clean_text.split('.')[0]
                    time_sec = self.time_to_sec(time_part)
                    if time_sec:
                        break

            if name and time_sec:
                rider_id = "r_" + hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
                if not any(r.rider_id == rider_id for r in results):
                    results.append(Result(
                        rider_id=rider_id,
                        rider_name=name,
                        time_sec=time_sec,
                        status="FIN",
                    ))

        return results
