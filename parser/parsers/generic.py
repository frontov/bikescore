import hashlib
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from parser.parsers.base import BaseParser
from parser.models import Result

class GenericParser(BaseParser):
    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        # Handles everything else
        return True

    def parse(self, url: str, page: Page) -> List[Result]:
        print(f"GenericParser: Scraping race {url}")
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
        if name_idx == -1: name_idx = 3
        if time_idx == -1: time_idx = 4

        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > max(name_idx, time_idx):
                name_col = cols[name_idx].text.strip()
                name = name_col.split('\n')[0].strip()

                time_col = cols[time_idx].text.strip()
                time_sec = self.time_to_sec(time_col)

                if name and time_sec:
                    rider_id = "r_" + hashlib.md5(name.encode('utf-8')).hexdigest()[:8]

                    # Check for duplicates in current race
                    if not any(r.rider_id == rider_id for r in results):
                        results.append(Result(
                            rider_id=rider_id,
                            rider_name=name,
                            time_sec=time_sec,
                            status="FIN",
                        ))
        return results
