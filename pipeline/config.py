"""Environment-driven configuration for the digest pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Config:
    # News
    newsapi_key: str | None = None
    news_query: str = "actualidad"
    news_country: str = "cl"
    news_page_size: int = 8
    rss_feeds: list[str] = field(default_factory=list)

    # Weather
    openweather_api_key: str | None = None
    weather_city: str = "Santiago"
    weather_country: str = "CL"
    weather_units: str = "metric"

    # Deals
    deals_keywords: list[str] = field(default_factory=list)
    deals_per_store: int = 5

    # GPT summary
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Email delivery
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_to: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            newsapi_key=os.getenv("NEWSAPI_KEY"),
            news_query=os.getenv("NEWS_QUERY", "actualidad"),
            news_country=os.getenv("NEWS_COUNTRY", "cl"),
            news_page_size=int(os.getenv("NEWS_PAGE_SIZE", "8")),
            rss_feeds=_split_csv(os.getenv("NEWS_RSS_FEEDS")),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            weather_city=os.getenv("WEATHER_CITY", "Santiago"),
            weather_country=os.getenv("WEATHER_COUNTRY", "CL"),
            weather_units=os.getenv("WEATHER_UNITS", "metric"),
            deals_keywords=_split_csv(os.getenv("DEALS_KEYWORDS")) or ["notebook"],
            deals_per_store=int(os.getenv("DEALS_PER_STORE", "5")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            email_from=os.getenv("EMAIL_FROM"),
            email_to=_split_csv(os.getenv("EMAIL_TO")),
        )
