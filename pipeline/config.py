"""Environment-driven configuration for the digest pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env(key: str, default: str = "") -> str:
    """Like os.getenv, but treats an empty string (e.g. an unset GitHub Actions
    secret/variable, which is interpolated as "") the same as an unset var."""
    return os.environ.get(key) or default


def _env_or_none(key: str) -> str | None:
    return os.environ.get(key) or None


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
            newsapi_key=_env_or_none("NEWSAPI_KEY"),
            news_query=_env("NEWS_QUERY", "actualidad"),
            news_country=_env("NEWS_COUNTRY", "cl"),
            news_page_size=int(_env("NEWS_PAGE_SIZE", "8")),
            rss_feeds=_split_csv(_env_or_none("NEWS_RSS_FEEDS")),
            openweather_api_key=_env_or_none("OPENWEATHER_API_KEY"),
            weather_city=_env("WEATHER_CITY", "Santiago"),
            weather_country=_env("WEATHER_COUNTRY", "CL"),
            weather_units=_env("WEATHER_UNITS", "metric"),
            deals_keywords=_split_csv(_env_or_none("DEALS_KEYWORDS")) or ["notebook"],
            deals_per_store=int(_env("DEALS_PER_STORE", "5")),
            openai_api_key=_env_or_none("OPENAI_API_KEY"),
            openai_model=_env("OPENAI_MODEL", "gpt-4o-mini"),
            smtp_host=_env_or_none("SMTP_HOST"),
            smtp_port=int(_env("SMTP_PORT", "587")),
            smtp_user=_env_or_none("SMTP_USER"),
            smtp_password=_env_or_none("SMTP_PASSWORD"),
            email_from=_env_or_none("EMAIL_FROM"),
            email_to=_split_csv(_env_or_none("EMAIL_TO")),
        )
