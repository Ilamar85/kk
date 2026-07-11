"""Fetch current weather conditions from OpenWeatherMap."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

from pipeline.config import Config

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@dataclass
class WeatherReport:
    city: str
    description: str
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float


def get_weather(config: Config) -> WeatherReport | None:
    if not config.openweather_api_key:
        return None
    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={
                "q": f"{config.weather_city},{config.weather_country}",
                "appid": config.openweather_api_key,
                "units": config.weather_units,
                "lang": "es",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        weather = (data.get("weather") or [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        return WeatherReport(
            city=data.get("name", config.weather_city),
            description=weather.get("description", ""),
            temp=main.get("temp", 0.0),
            feels_like=main.get("feels_like", 0.0),
            humidity=main.get("humidity", 0),
            wind_speed=wind.get("speed", 0.0),
        )
    except requests.RequestException as exc:
        logger.warning("OpenWeatherMap fetch failed: %s", exc)
        return None
