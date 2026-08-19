#!/usr/bin/env python3
"""
Monitor de precios Goodnites L/XL (27-57 kg) - mercado chileno.

Extrae precios sin usar IA ni tokens: lee meta-tags Open Graph del HTML
y APIs publicas JSON. Costo por ejecucion: ~0.
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

TZ_CL = timezone(timedelta(hours=-4))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "es-CL,es;q=0.9"}
TIMEOUT = 20

HIST = Path("historico.json")
UMBRAL_ALERTA = 700  # CLP por unidad: bajo esto, avisar


# ---------------------------------------------------------------- utilidades

def meta(html: str, *props: str):
    """Devuelve el content de la primera meta-tag que coincida."""
    for p in props:
        pat = (r'<meta[^>]+(?:property|name)=["\']' + re.escape(p) +
               r'["\'][^>]+content=["\']([^"\']+)["\']')
        m = re.search(pat, html, re.I)
        if not m:
            pat = (r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+'
                   r'(?:property|name)=["\']' + re.escape(p) + r'["\']')
            m = re.search(pat, html, re.I)
        if m:
            return m.group(1).strip()
    return None


def a_int(valor):
    if valor is None:
        return None
    limpio = re.sub(r"[^\d.]", "", str(valor))
    if not limpio:
        return None
    try:
        return int(round(float(limpio)))
    except ValueError:
        return None


def get(url, **kw):
    return requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kw)


# ------------------------------------------------------------ extractores

def og_generico(url, unidades, tienda, prop_precio, prop_normal=None,
                prop_stock=None):
    """Sitios que publican precio en Open Graph (Salcobrand, Jumpseller,
    Tiendanube). Verificado funcionando en los tres."""
    html = get(url).text
    precio = a_int(meta(html, *prop_precio))
    normal = a_int(meta(html, *prop_normal)) if prop_normal else None
    stock = meta(html, *prop_stock) if prop_stock else None
    return {
        "tienda": tienda,
        "unidades": unidades,
        "precio": precio,
        "precio_normal": normal,
        "stock": stock,
        "url": url,
    }


def vtex(url_base, slug, unidades, tienda):
    """Jumbo, Santa Isabel y otros VTEX exponen catalogo JSON publico."""
    api = f"{url_base}/api/catalog_system/pub/products/search/{slug}/p"
    data = get(api).json()
    if not data:
        raise ValueError("sin resultados en API VTEX")
    item = data[0]["items"][0]
    oferta = item["sellers"][0]["commertialOffer"]
    return {
        "tienda": tienda,
        "unidades": unidades,
        "precio": a_int(oferta.get("Price")),
        "precio_normal": a_int(oferta.get("ListPrice")),
        "stock": "in stock" if oferta.get("AvailableQuantity", 0) > 0 else "agotado",
        "url": url_base + "/" + slug + "/p",
    }


def mercadolibre(product_id, unidades, tienda):
    """API publica de catalogo. Puede requerir token segun politica vigente."""
    api = f"https://api.mercadolibre.com/products/{product_id}"
    r = get(api)
    if r.status_code != 200:
        raise ValueError(f"HTTP {r.status_code} (posible requerimiento de token)")
    d = r.json()
    precio = None
    if d.get("buy_box_winner"):
        precio = a_int(d["buy_box_winner"].get("price"))
    if precio is None and d.get("price"):
        precio = a_int(d["price"])
    return {
        "tienda": tienda,
        "unidades": unidades,
        "precio": precio,
        "precio_normal": None,
        "stock": d.get("status"),
        "url": d.get("permalink") or
               f"https://www.mercadolibre.cl/p/{product_id}",
    }


# ------------------------------------------------------------------ fuentes
# Verificadas funcionando: Salcobrand, Jesbriel, La Panalera.
# Best-effort (ajustar si cambia el sitio): Jumbo, Mercado Libre.

FUENTES = [
    ("Salcobrand", lambda: og_generico(
        "https://salcobrand.cl/products/"
        "ropa-interior-desechable-goodnites-unisex-talla-l-11-unidades",
        11, "Salcobrand",
        prop_precio=("product:sale_price:amount",),
        prop_normal=("product:price:amount", "og:price:amount"),
        prop_stock=("product:availability",))),

    ("Jesbriel 11un", lambda: og_generico(
        "https://www.jesbrielpanales.cl/productos/"
        "panal-goodnites-calzon-27-57kg-talla-l-xl-11-unidades/",
        11, "Jesbriel",
        prop_precio=("tiendanube:price",),
        prop_stock=("tiendanube:stock",))),

    ("Jesbriel caja 44un", lambda: og_generico(
        "https://www.jesbrielpanales.cl/productos/"
        "panal-goodnites-calzon-27-57kg-talla-l-xl-4-x-11-unidades-caja/",
        44, "Jesbriel (caja)",
        prop_precio=("tiendanube:price",),
        prop_stock=("tiendanube:stock",))),

    ("La Panalera 11un", lambda: og_generico(
        "https://www.lapanalera.cl/panal-goodnites-pants-talla-l-xl-11-unidades",
        11, "La Panalera",
        prop_precio=("product:price:amount",),
        prop_normal=("product:original_price:amount",),
        prop_stock=("product:availability",))),

    ("La Panalera 22un", lambda: og_generico(
        "https://www.lapanalera.cl/panal-goodnites-pants-talla-l-xl-22-unidades",
        22, "La Panalera",
        prop_precio=("product:price:amount",),
        prop_normal=("product:original_price:amount",),
        prop_stock=("product:availability",))),

    ("La Panalera 44un", lambda: og_generico(
        "https://www.lapanalera.cl/panal-goodnites-pants-talla-l-xl-44-unidades",
        44, "La Panalera",
        prop_precio=("product:price:amount",),
        prop_normal=("product:original_price:amount",),
        prop_stock=("product:availability",))),

    ("Jumbo", lambda: vtex(
        "https://www.jumbo.cl",
        "ropa-interior-goodnites-talla-l-xl-11-unidades",
        11, "Jumbo")),

    ("Mercado Libre", lambda: mercadolibre(
        "MLC24841527", 11, "Mercado Libre")),
]


# -------------------------------------------------------------------- main

def recolectar():
    filas, errores = [], []
    for nombre, fn in FUENTES:
        try:
            r = fn()
            if r.get("precio"):
                r["unitario"] = round(r["precio"] / r["unidades"])
                filas.append(r)
            else:
                errores.append(f"{nombre}: precio no encontrado")
        except Exception as e:
            errores.append(f"{nombre}: {type(e).__name__} - {e}")
    filas.sort(key=lambda x: x["unitario"])
    return filas, errores


def formato_clp(n):
    return f"${n:,.0f}".replace(",", ".")


def tabla_md(filas):
    out = ["| Tienda | Un. | Precio | $/unidad | Stock |",
           "|---|---|---|---|---|"]
    for f in filas:
        precio = formato_clp(f["precio"])
        if f.get("precio_normal") and f["precio_normal"] > f["precio"]:
            dcto = round((1 - f["precio"] / f["precio_normal"]) * 100)
            precio += f" (-{dcto}%)"
        stock = f.get("stock") or "?"
        out.append(f"| {f['tienda']} | {f['unidades']} | {precio} | "
                   f"**{formato_clp(f['unitario'])}** | {stock} |")
    return "\n".join(out)


def main():
    ahora = datetime.now(TZ_CL)
    filas, errores = recolectar()

    if not filas:
        print("ERROR: ninguna fuente entrego precio.")
        for e in errores:
            print("  -", e)
        return 1

    historico = json.loads(HIST.read_text()) if HIST.exists() else []
    previo = historico[-1] if historico else None

    reporte = [f"# Precios Goodnites L/XL - {ahora:%d-%m-%Y %H:%M}", "",
               tabla_md(filas), ""]

    mejor = filas[0]
    reporte.append(f"**Mejor opcion:** {mejor['tienda']} - "
                   f"{formato_clp(mejor['unitario'])}/unidad")
    reporte.append(f"{mejor['url']}")

    # comparacion con la corrida anterior
    if previo:
        antes = {f["tienda"] + str(f["unidades"]): f["unitario"]
                 for f in previo["filas"]}
        cambios = []
        for f in filas:
            k = f["tienda"] + str(f["unidades"])
            if k in antes and antes[k] != f["unitario"]:
                delta = f["unitario"] - antes[k]
                signo = "sube" if delta > 0 else "baja"
                cambios.append(f"- {f['tienda']} ({f['unidades']} un): "
                               f"{signo} {formato_clp(abs(delta))}/un "
                               f"({formato_clp(antes[k])} -> "
                               f"{formato_clp(f['unitario'])})")
        if cambios:
            reporte += ["", "## Cambios vs. corrida anterior", *cambios]

    if mejor["unitario"] < UMBRAL_ALERTA:
        reporte += ["", f"## ALERTA: bajo el umbral de "
                        f"{formato_clp(UMBRAL_ALERTA)}/unidad"]

    if errores:
        reporte += ["", "## Fuentes sin dato", *[f"- {e}" for e in errores]]

    texto = "\n".join(reporte)
    print(texto)

    historico.append({"fecha": ahora.isoformat(), "filas": filas})
    HIST.write_text(json.dumps(historico[-52:], ensure_ascii=False, indent=2))
    Path("ultimo_reporte.md").write_text(texto)

    # marca para que el workflow decida si abrir issue
    Path("alerta.flag").write_text(
        "1" if mejor["unitario"] < UMBRAL_ALERTA else "0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
