"""Entry point: fetch news/weather/deals, summarize with GPT, and email the digest."""
from __future__ import annotations

import datetime
import logging
from pathlib import Path

from dotenv import load_dotenv

from pipeline.config import Config
from pipeline.delivery.email_sender import send_email
from pipeline.sources.deals.runner import get_deals
from pipeline.sources.news import get_news
from pipeline.sources.weather import get_weather
from pipeline.summarizer import generate_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def run() -> str:
    load_dotenv()
    config = Config.from_env()

    logger.info("Fetching news...")
    news = get_news(config)
    logger.info("Fetched %d news items", len(news))

    logger.info("Fetching weather...")
    weather = get_weather(config)

    logger.info("Scraping deals...")
    deals = get_deals(config)
    logger.info("Found %d deals", len(deals))

    logger.info("Generating summary with GPT...")
    summary = generate_summary(config, news, weather, deals)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    output_path = output_dir / f"digest-{today}.md"
    output_path.write_text(summary, encoding="utf-8")
    logger.info("Digest written to %s", output_path)

    try:
        send_email(config, subject=f"Resumen diario - {today}", markdown_body=summary)
    except RuntimeError as exc:
        logger.warning("Skipping email delivery: %s", exc)

    return summary


if __name__ == "__main__":
    run()
