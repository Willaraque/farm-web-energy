from Librerias.lib import *
from Librerias.vars import *
from fastapi import APIRouter, HTTPException
from typing import List

'''
    #GET -> pide datos
    #POST -> crea datos
    #PUT -> Actualiza datos
    #DELETE -> Elimina datos 
    
'''

app_prices = APIRouter()


# @app_prices.post("/market-data", response_model=List[MarketDataResponse])
@app_prices.post("/market-data")
async def get_market_data(data:MarketData):
    # return {'message':'correcto'}
    data = await get_all_prices(data)
    df_dict = data.to_dict(orient='records')
    if df_dict:
        return df_dict
        # return [MarketDataResponse(**record) for record in df_dict]
    else: raise HTTPException(status_code=409, detail='Something went wrong')

