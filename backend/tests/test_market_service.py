import pandas as pd
import pytest

from app.services.market import _format_market_data, _normalize_markets


def test_market_names_are_translated_for_pcrenergy() -> None:
    assert _normalize_markets(["diario", "intradiario", "daily"]) == ["daily", "intradaily"]


def test_unknown_markets_are_rejected() -> None:
    with pytest.raises(ValueError):
        _normalize_markets(["desconocido"])


def test_pcrenergy_market_frame_keeps_frontend_contract() -> None:
    source = pd.DataFrame({"date": ["2026-08-11T10:00:00"], "season": [1], "value": [82.45], "market": ["daily"], "name": ["Precio marginal español"]})
    result = _format_market_data(source)
    assert result.to_dict(orient="records") == [
        {
            "Fecha": "2026-08-11",
            "Mes": 8,
            "Hora": 10,
            "Season": 1,
            "Tipo": "Precio marginal español",
            "Mercado": "diario",
            "price": 82.45,
            "Precio_Español": 82.45,
        }
    ]
