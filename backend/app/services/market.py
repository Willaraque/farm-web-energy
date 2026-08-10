"""Consulta y adaptación de datos del mercado ibérico."""

from __future__ import annotations

import asyncio

import pandas as pd
from pcrenergy import Omie

from app.core.mongo import mongo_client
from app.schemas.models import MarketData

MARKET_NAMES = {
    "diario": "daily",
    "daily": "daily",
    "intradiario": "intradaily",
    "intradaily": "intradaily",
}
PUBLIC_MARKET_NAMES = {"daily": "diario", "intradaily": "intradiario"}
PRICE_COLUMN = "price"
LEGACY_PRICE_COLUMN = "Precio_Español"


def _normalize_markets(markets: list[str]) -> list[str]:
    normalized = [
        MARKET_NAMES[value.strip().lower()]
        for value in markets
        if value.strip().lower() in MARKET_NAMES
    ]
    if not normalized:
        raise ValueError("Debe indicarse al menos un mercado OMIE válido")
    return list(dict.fromkeys(normalized))


def _format_market_data(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    if "date" not in frame or "value" not in frame:
        raise ValueError("pcrenergy devolvió un formato de mercado no reconocido")

    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    result["Fecha"] = result["date"].dt.strftime("%Y-%m-%d")
    result["Mes"] = result["date"].dt.month
    result["Hora"] = result["date"].dt.hour
    result[PRICE_COLUMN] = pd.to_numeric(result["value"], errors="coerce")
    result[LEGACY_PRICE_COLUMN] = result[PRICE_COLUMN]

    market = result.get("market", "daily")
    result["Mercado"] = (
        market.map(PUBLIC_MARKET_NAMES).fillna(market)
        if isinstance(market, pd.Series)
        else PUBLIC_MARKET_NAMES.get(market, market)
    )
    result["Tipo"] = result.get("name", "Precio marginal español")
    result["Season"] = result.get("season", 0)

    columns = [
        "Fecha",
        "Mes",
        "Hora",
        "Season",
        "Tipo",
        "Mercado",
        PRICE_COLUMN,
        LEGACY_PRICE_COLUMN,
    ]
    return result.loc[:, columns].dropna(subset=[PRICE_COLUMN]).reset_index(drop=True)


async def get_all_prices(data: MarketData) -> pd.DataFrame:
    if "OMIE" not in data.tipo.upper():
        raise ValueError("El endpoint de precios admite actualmente datos OMIE")

    markets = _normalize_markets(data.mercados)
    repository = Omie(
        start=data.desde,
        end=data.hasta,
        markets=markets,
        mongoclient=mongo_client,
        warning=data.warning,
    )
    frame = await asyncio.to_thread(
        repository.get_market_indicators,
        markets=markets,
        filenames="Precio marginal español",
    )
    return _format_market_data(frame)
