# Digest diario: noticias, clima y ofertas

Pipeline que cada día:

1. Obtiene noticias (NewsAPI + feeds RSS, ej. Reuters).
2. Obtiene el clima actual (OpenWeatherMap).
3. Scrapea ofertas en Falabella, Paris, Ripley y MercadoLibre con Playwright, descartando publicaciones de MercadoLibre con envío internacional (que implican pagos extra de aduana/aranceles) y quedándose solo con entrega nacional en Chile.
4. Genera un resumen en Markdown con GPT (OpenAI API).
5. Envía el resumen por correo (HTML + texto plano).

Pensado para ejecutarse por cron, GitHub Actions o n8n.

## Estructura

```
pipeline/
  config.py              # configuración vía variables de entorno
  main.py                 # orquestador (python -m pipeline.main)
  summarizer.py            # prompt + llamada a OpenAI, produce Markdown
  sources/
    news.py                # NewsAPI + RSS
    weather.py              # OpenWeatherMap
    deals/
      base.py                # tipos comunes (Deal, BaseDealScraper)
      falabella.py, paris.py, ripley.py, mercadolibre.py   # scrapers Playwright por tienda
      runner.py               # orquesta el navegador y agrega resultados
  delivery/
    email_sender.py          # renderiza Markdown->HTML y envía por SMTP
```

## Configuración

1. `pip install -r requirements.txt`
2. `playwright install chromium`
3. Copia `.env.example` a `.env` y completa las variables:

| Variable | Descripción |
|---|---|
| `NEWSAPI_KEY` | API key de [NewsAPI](https://newsapi.org/) (opcional si solo usas RSS) |
| `NEWS_RSS_FEEDS` | URLs de feeds RSS separadas por coma |
| `OPENWEATHER_API_KEY` | API key de [OpenWeatherMap](https://openweathermap.org/api) |
| `WEATHER_CITY` / `WEATHER_COUNTRY` | Ciudad a consultar |
| `DEALS_KEYWORDS` | Palabras clave a buscar en cada tienda, separadas por coma |
| `OPENAI_API_KEY` | API key de OpenAI, usada para redactar el resumen |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Credenciales SMTP para el envío |
| `EMAIL_FROM`, `EMAIL_TO` | Remitente y destinatario(s) (coma-separados) |

## Ejecutar localmente

```bash
python -m pipeline.main
```

El resumen se guarda en `output/digest-<fecha>.md` y, si el SMTP está configurado, se envía por correo.

## Automatización

`.github/workflows/daily-digest.yml` ejecuta el pipeline todos los días vía GitHub Actions.
Configura los secrets (`NEWSAPI_KEY`, `OPENWEATHER_API_KEY`, `OPENAI_API_KEY`, `SMTP_*`, `EMAIL_FROM`, `EMAIL_TO`)
y, opcionalmente, las variables (`NEWS_QUERY`, `WEATHER_CITY`, `DEALS_KEYWORDS`, etc.) en la configuración
del repositorio (Settings → Secrets and variables → Actions).

## Notas sobre el scraping

Los scrapers de Falabella, Paris, Ripley y MercadoLibre dependen de la estructura HTML actual de cada sitio.
Si un sitio cambia su diseño, ese scraper puede dejar de encontrar resultados; el pipeline sigue
funcionando igual con los datos de las otras tiendas (cada scraper falla de forma aislada y queda
registrado en el log).

En MercadoLibre, cada publicación se filtra por texto: si la tarjeta del producto menciona envío
internacional, aduana, aranceles, "llega de [país extranjero]" u otro indicador de compra
transfronteriza, la oferta se descarta (ver `INTERNATIONAL_MARKERS` en
`pipeline/sources/deals/mercadolibre.py`). Solo quedan publicaciones de entrega nacional en Chile.

## Extender a otros canales de envío (Telegram, WhatsApp, Slack, Notion)

`pipeline/main.py` ya genera el Markdown final antes de enviarlo por correo. Para agregar otro canal,
crea un módulo en `pipeline/delivery/` (ej. `telegram_sender.py`) con una función `send_*(config, subject, markdown_body)`
y llámala desde `run()` en `pipeline/main.py`.

## Monitor de precios Goodnites (`goodnites/`)

Script independiente que compara el precio por unidad de pañales Goodnites L/XL (27-57 kg) en
Salcobrand, Jesbriel, La Panalera, Jumbo y Mercado Libre, sin usar IA: lee meta-tags Open Graph
y APIs JSON públicas de cada tienda.

```
goodnites/
  monitor_precios.py     # recolecta precios y genera el reporte
  historico.json          # últimas 52 corridas (se actualiza y commitea automáticamente)
  ultimo_reporte.md        # reporte Markdown de la corrida más reciente
  alerta.flag              # "1"/"0": si el mejor precio unitario está bajo el umbral
```

Ejecutar localmente:

```bash
cd goodnites
python monitor_precios.py
```

`.github/workflows/goodnites-price-monitor.yml` corre el script todos los días vía GitHub Actions,
commitea el histórico actualizado y, si `alerta.flag` marca `1` (precio unitario bajo
`UMBRAL_ALERTA`, definido en el script), abre o comenta un issue etiquetado `goodnites-alerta`
con el reporte.
