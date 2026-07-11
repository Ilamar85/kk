"""Fetch news headlines from NewsAPI and RSS feeds."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import feedparser
import requests

from pipeline.config import Config

logger = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


@dataclass
class NewsItem:
    title: str
    source: str
    url: str
    summary: str = ""


def fetch_from_newsapi(config: Config) -> list[NewsItem]:
    if not config.newsapi_key:
        return []
    try:
        response = requests.get(
            NEWSAPI_URL,
            params={
                "apiKey": config.newsapi_key,
                "q": config.news_query,
                "country": config.news_country,
                "pageSize": config.news_page_size,
            },
            timeout=15,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [
            NewsItem(
                title=a.get("title", "").strip(),
                source=(a.get("source") or {}).get("name", "NewsAPI"),
                url=a.get("url", ""),
                summary=a.get("description") or "",
            )
            for a in articles
            if a.get("title")
        ]
    except requests.RequestException as exc:
        logger.warning("NewsAPI fetch failed: %s", exc)
        return []


def fetch_from_rss(config: Config) -> list[NewsItem]:
    items: list[NewsItem] = []
    for feed_url in config.rss_feeds:
        try:
            parsed = feedparser.parse(feed_url)
            source_name = parsed.feed.get("title", feed_url)
            for entry in parsed.entries[:config.news_page_size]:
                items.append(
                    NewsItem(
                        title=entry.get("title", "").strip(),
                        source=source_name,
                        url=entry.get("link", ""),
                        summary=entry.get("summary", ""),
                    )
                )
        except Exception as exc:  # feedparser can raise various things per feed
            logger.warning("RSS fetch failed for %s: %s", feed_url, exc)
    return items


def get_news(config: Config) -> list[NewsItem]:
    items = fetch_from_newsapi(config) + fetch_from_rss(config)
    seen_titles: set[str] = set()
    deduped = []
    for item in items:
        if item.title and item.title not in seen_titles:
            seen_titles.add(item.title)
            deduped.append(item)
    return deduped
