"""Shared types for retail-site deal scrapers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from playwright.sync_api import Page


@dataclass
class Deal:
    store: str
    title: str
    price: str
    original_price: str | None
    discount_pct: str | None
    url: str


class BaseDealScraper(ABC):
    store_name: str = "unknown"

    @abstractmethod
    def search_url(self, keyword: str) -> str:
        """Return the search results URL for a given keyword."""

    @abstractmethod
    def extract_deals(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        """Scrape the already-loaded search results page for deals."""

    def scrape(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        page.goto(self.search_url(keyword), wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        return self.extract_deals(page, keyword, limit)
