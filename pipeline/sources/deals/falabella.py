"""Deal scraper for falabella.com search results."""
from __future__ import annotations

import logging
from urllib.parse import quote

from playwright.sync_api import Page

from .base import BaseDealScraper, Deal

logger = logging.getLogger(__name__)


class FalabellaScraper(BaseDealScraper):
    store_name = "Falabella"

    def search_url(self, keyword: str) -> str:
        return f"https://www.falabella.com/falabella-cl/search?Ntt={quote(keyword)}"

    def extract_deals(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        deals: list[Deal] = []
        pods = page.query_selector_all("div[data-pod], div.pod")[:limit]
        for pod in pods:
            title_el = pod.query_selector("[data-pod-title], b.pod-title, .pod-title")
            link_el = pod.query_selector("a")
            price_el = pod.query_selector(
                "li[data-cmr-price], li[data-event-price], span.copy10, .prices-0"
            )
            original_el = pod.query_selector("li[data-normal-price], .prices-1")
            discount_el = pod.query_selector(".discount-badge, [data-discount]")

            title = title_el.inner_text().strip() if title_el else None
            price = price_el.inner_text().strip() if price_el else None
            if not title or not price:
                continue

            href = link_el.get_attribute("href") if link_el else None
            url = href if (href and href.startswith("http")) else f"https://www.falabella.com{href or ''}"

            deals.append(
                Deal(
                    store=self.store_name,
                    title=title,
                    price=price,
                    original_price=original_el.inner_text().strip() if original_el else None,
                    discount_pct=discount_el.inner_text().strip() if discount_el else None,
                    url=url,
                )
            )
        return deals
