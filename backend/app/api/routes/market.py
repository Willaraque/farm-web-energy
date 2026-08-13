import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.models import MarketData
from app.services.market import get_all_prices
from app.repositories.tokens import get_user_active_current

logger = logging.getLogger(__name__)
app_prices = APIRouter(
    tags=["market-data"], dependencies=[Depends(get_user_active_current)]
)


@app_prices.post("/market-data")
async def get_market_data(payload: MarketData) -> list[dict]:
    try:
        frame = await get_all_prices(payload)
    except (ValueError, KeyError) as error:
        raise HTTPException(
            422, "No se pudieron procesar los datos para el periodo indicado"
        ) from error
    except Exception as error:
        logger.exception("Error inesperado consultando datos de mercado")
        raise HTTPException(
            503, "El servicio de mercado no está disponible temporalmente"
        ) from error
    return frame.to_dict(orient="records")
