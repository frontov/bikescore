from typing import Type
from parser.parsers.base import BaseParser
from parser.parsers.timingband import TimingbandParser
from parser.parsers.sportident import SportidentParser
from parser.parsers.resultszone import ResultsZoneParser
from parser.parsers.generic import GenericParser

def get_parser(url: str) -> BaseParser:
    """Returns an instance of the appropriate parser for the given URL."""
    # The order matters. GenericParser should be last as it handles everything.
    parsers: list[Type[BaseParser]] = [
        TimingbandParser,
        SportidentParser,
        ResultsZoneParser,
        GenericParser
    ]

    for parser_cls in parsers:
        if parser_cls.can_handle_url(url):
            return parser_cls()

    return GenericParser() # Fallback
