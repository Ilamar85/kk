"""Builds a Markdown digest from raw data using the OpenAI API."""
from __future__ import annotations

from openai import OpenAI

from pipeline.config import Config
from pipeline.sources.deals.base import Deal
from pipeline.sources.news import NewsItem
from pipeline.sources.weather import WeatherReport

SYSTEM_PROMPT = (
    "Eres un asistente que redacta un resumen diario breve y ameno en español, "
    "en formato Markdown, con tres secciones tituladas '## Noticias', '## Clima' "
    "y '## Ofertas'. Se conciso: usa listas con viñetas, evita relleno, e incluye "
    "los enlaces (URL) de cada noticia y oferta como links Markdown."
)


def _format_news(news: list[NewsItem]) -> str:
    if not news:
        return "Sin noticias disponibles hoy."
    lines = [f"- **{n.title}** ({n.source}): {n.summary} [Leer más]({n.url})" for n in news]
    return "\n".join(lines)


def _format_weather(weather: WeatherReport | None) -> str:
    if weather is None:
        return "Datos de clima no disponibles."
    return (
        f"{weather.city}: {weather.description}, {weather.temp}°C "
        f"(sensación {weather.feels_like}°C), humedad {weather.humidity}%, "
        f"viento {weather.wind_speed} m/s."
    )


def _format_deals(deals: list[Deal]) -> str:
    if not deals:
        return "Sin ofertas disponibles hoy."
    lines = []
    for d in deals:
        discount = f" ({d.discount_pct})" if d.discount_pct else ""
        original = f" ~~{d.original_price}~~" if d.original_price else ""
        lines.append(f"- [{d.store}] **{d.title}**: {d.price}{original}{discount} [Ver oferta]({d.url})")
    return "\n".join(lines)


def build_user_prompt(news: list[NewsItem], weather: WeatherReport | None, deals: list[Deal]) -> str:
    return (
        "Datos crudos para el resumen de hoy:\n\n"
        f"### Noticias\n{_format_news(news)}\n\n"
        f"### Clima\n{_format_weather(weather)}\n\n"
        f"### Ofertas\n{_format_deals(deals)}\n"
    )


def generate_summary(
    config: Config,
    news: list[NewsItem],
    weather: WeatherReport | None,
    deals: list[Deal],
) -> str:
    if not config.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=config.openai_api_key)
    response = client.chat.completions.create(
        model=config.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(news, weather, deals)},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content or ""
