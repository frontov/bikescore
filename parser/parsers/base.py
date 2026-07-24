from abc import ABC, abstractmethod
from typing import List
from playwright.sync_api import Page
from parser.models import Result

class BaseParser(ABC):
    @classmethod
    @abstractmethod
    def can_handle_url(cls, url: str) -> bool:
        """Returns True if this parser can handle the given URL."""
        pass

    @abstractmethod
    def parse(self, url: str, page: Page) -> List[Result]:
        """Parses the given URL using the playwright page and returns a list of Results."""
        pass

    @staticmethod
    def time_to_sec(time_str: str) -> int | None:
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2].replace(',', '.')))
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(float(parts[1].replace(',', '.')))
        except Exception:
            pass
        return None
