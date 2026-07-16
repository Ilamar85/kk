"""Deal scraper for paris.cl (VTEX-based) search results."""
from __future__ import annotations

import logging
from urllib.parse import quote

from playwright.sync_api import Page

from .base import BaseDealScraper, Deal

logger = logging.getLogger(__name__)


class ParisScraper(BaseDealScraper):
    store_name = "Paris"

    def search_url(self, keyword: str) -> str:
        return f"https://www.paris.cl/{quote(keyword)}?_q={quote(keyword)}&map=ft"

    def extract_deals(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        deals: list[Deal] = []
        cards = page.query_selector_all(
            "[class*='product-summary'], article.vtex-product-summary-2-x-element"
        )[:limit]
        for card in cards:
            title_el = card.query_selector("[class*='productBrand'], [class*='productName'], h3, h2")
            link_el = card.query_selector("a")
            price_el = card.query_selector(
                "[class*='sellingPriceValue'], [class*='sellingPrice'], [class*='bestPrice']"
            )
            original_el = card.query_selector("[class*='listPriceValue'], [class*='listPrice']")

            title = title_el.inner_text().strip() if title_el else None
            price = price_el.inner_text().strip() if price_el else None
            if not title or not price:
                continue

            href = link_el.get_attribute("href") if link_el else None
            url = href if (href and href.startswith("http")) else f"https://www.paris.cl{href or ''}"

            deals.append(
                Deal(
                    store=self.store_name,
                    title=title,
                    price=price,
                    original_price=original_el.inner_text().strip() if original_el else None,
                    discount_pct=None,
                    url=url,
                )
            )
        return deals
