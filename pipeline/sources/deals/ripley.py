"""Deal scraper for simple.ripley.cl search results."""
from __future__ import annotations

import logging
from urllib.parse import quote

from playwright.sync_api import Page

from .base import BaseDealScraper, Deal

logger = logging.getLogger(__name__)


class RipleyScraper(BaseDealScraper):
    store_name = "Ripley"

    def search_url(self, keyword: str) -> str:
        return f"https://simple.ripley.cl/search?source=search&terms={quote(keyword)}"

    def extract_deals(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        deals: list[Deal] = []
        cards = page.query_selector_all(
            "[class*='catalog-product-item'], .catalog-product"
        )[:limit]
        for card in cards:
            title_el = card.query_selector("[class*='catalog-product-details__name'], b, h2, h3")
            link_el = card.query_selector("a")
            price_el = card.query_selector(
                "[class*='catalog-prices__offer-price'], [class*='price']"
            )
            original_el = card.query_selector(
                "[class*='catalog-prices__list-price'], [class*='normal-price']"
            )
            discount_el = card.query_selector("[class*='discount']")

            title = title_el.inner_text().strip() if title_el else None
            price = price_el.inner_text().strip() if price_el else None
            if not title or not price:
                continue

            href = link_el.get_attribute("href") if link_el else None
            url = href if (href and href.startswith("http")) else f"https://simple.ripley.cl{href or ''}"

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
