"""Deal scraper for listado.mercadolibre.cl search results.

Only listings with national (Chilean) delivery are kept: any result whose
card text mentions international/cross-border shipping, customs, tariffs or
extra payments from abroad is discarded, since those require additional
charges on arrival that regular national listings don't.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import quote

from playwright.sync_api import Page

from .base import BaseDealScraper, Deal

logger = logging.getLogger(__name__)

INTERNATIONAL_MARKERS = (
    "internacional",
    "importado",
    "importaci",
    "extranjero",
    "aduana",
    "arancel",
    "cross border",
    "cross-border",
    "global selling",
    "llega de estados unidos",
    "llega de china",
    "llega de brasil",
    "llega de miami",
    "compra protegida internacional",
    "pago de impuestos",
    "impuestos de importaci",
)


def _is_national_delivery(card_text: str) -> bool:
    normalized = card_text.lower()
    return not any(marker in normalized for marker in INTERNATIONAL_MARKERS)


class MercadoLibreScraper(BaseDealScraper):
    store_name = "MercadoLibre"

    def search_url(self, keyword: str) -> str:
        slug = re.sub(r"\s+", "-", keyword.strip())
        return f"https://listado.mercadolibre.cl/{quote(slug)}"

    def extract_deals(self, page: Page, keyword: str, limit: int) -> list[Deal]:
        deals: list[Deal] = []
        cards = page.query_selector_all(
            "li.ui-search-layout__item, div.ui-search-result__wrapper"
        )
        for card in cards:
            if len(deals) >= limit:
                break

            card_text = card.inner_text()
            if not _is_national_delivery(card_text):
                continue

            title_el = card.query_selector(
                "h2.ui-search-item__title, .ui-search-item__title"
            )
            link_el = card.query_selector("a.ui-search-link, a.ui-search-item__group__element")
            price_el = card.query_selector(
                ".ui-search-price__second-line .andes-money-amount__fraction, "
                ".andes-money-amount__fraction"
            )
            original_price_el = card.query_selector(
                ".ui-search-price__original-value .andes-money-amount__fraction"
            )
            discount_el = card.query_selector(".ui-search-price__discount")

            title = title_el.inner_text().strip() if title_el else None
            price = price_el.inner_text().strip() if price_el else None
            if not title or not price:
                continue

            url = link_el.get_attribute("href") if link_el else None
            if not url:
                continue

            deals.append(
                Deal(
                    store=self.store_name,
                    title=title,
                    price=f"${price}",
                    original_price=f"${original_price_el.inner_text().strip()}" if original_price_el else None,
                    discount_pct=discount_el.inner_text().strip() if discount_el else None,
                    url=url,
                )
            )
        return deals
