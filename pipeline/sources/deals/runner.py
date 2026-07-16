"""Runs all deal scrapers under a single Playwright browser instance."""
from __future__ import annotations

import logging

from playwright.sync_api import sync_playwright

from pipeline.config import Config

from .base import Deal
from .falabella import FalabellaScraper
from .mercadolibre import MercadoLibreScraper
from .paris import ParisScraper
from .ripley import RipleyScraper

logger = logging.getLogger(__name__)

SCRAPERS = [FalabellaScraper(), ParisScraper(), RipleyScraper(), MercadoLibreScraper()]


def get_deals(config: Config) -> list[Deal]:
    if not config.deals_keywords:
        return []

    deals: list[Deal] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="es-CL",
            )
            page = context.new_page()
            for scraper in SCRAPERS:
                for keyword in config.deals_keywords:
                    try:
                        found = scraper.scrape(page, keyword, config.deals_per_store)
                        deals.extend(found)
                    except Exception as exc:
                        logger.warning(
                            "%s scraper failed for keyword '%s': %s",
                            scraper.store_name,
                            keyword,
                            exc,
                        )
            context.close()
        finally:
            browser.close()
    return deals
