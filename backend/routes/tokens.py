from Librerias.lib import *
from Librerias.vars import *
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import os



app_tokens = APIRouter()

  
@app_tokens.post("/token", response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm= Depends()) -> dict:
    USERS = await authenticate_user(form_data.username, form_data.password)
    if not USERS:
        raise  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = create_access_token(
        data={"sub": USERS.username}, expires_delta=access_token_expires
    )

    # refresh_token_expires = timedelta(minutes=int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')))
    # refresh_token = create_refresh_token(  # Si manejas refresh tokens
    #     data={"sub": USERS.username},
    #     expires_delta=refresh_token_expires
    # )

    dict_jwt = {
        "access_token": access_token,
        "token_type": "bearer",
        # "refresh_token": refresh_token  # Si manejas refresh tokens
    }

    info_jwt = await save_token(USERS.id, USERS.username, dict_jwt)
    return info_jwt

@app_tokens.get("/users/me")
async def read_users_me(user:  Annotated[dict,Depends(get_user_active_current)]): #Depends(get_current_user)
    del user.password #Eliminar la contraseña del usuario, para que no sea robada, aunque la ruta esté encriptada
    return user

# @app_tokens.post("/refresh")
# async def refresh_access_token(data:RefreshToken):
#     try:
#         refresh_token = data.refresh_token
#         payload = jwt.decode(refresh_token, key=str(os.getenv('REFRESH_TOKEN_SECRET')), algorithms=[str(os.getenv('ALGORITHM'))])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

#     new_access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
#     new_access_token = create_access_token(
#         data={"sub": username}, expires_delta=new_access_token_expires
#     )

#     dictRefresh_jwt = {"access_token": new_access_token,
#                     "token_type": "bearer"
#     }
#     refresh_jwt =  await update_token(refresh_token, dictRefresh_jwt)

#     return refresh_jwt

#-------------- Verificación del Token (verify-token) ----------
@app_tokens.post("/verify-token")
async def verify_token_endpoint(token_data: TokenData):
    token_status = await verify_token(token_data.token)
    if not token_status["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_status

@app_tokens.post("/refresh-token")
async def refresh_token_endpoint(refresh_data: RefreshTokenData):
    payload = await verify_refresh_token(refresh_data.refresh_token)
    # Aquí puedes agregar más lógica, como verificar si el refresh_token está en una lista permitida
    new_access_token = create_access_token(
        data={"sub": payload["sub"]},  # Incluye la información relevante del usuario
        expires_delta=timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    )

    dict_new_jwt = {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
    info_jwt = await update_token(refresh_data.refresh_token, dict_new_jwt)
    
    return info_jwt

@app_tokens.delete("/delete-token")
async def deleteToken(data: IdMongo):
    id = data.id
    bool_token = await drop_tokenBD(id)
    if not bool_token["valid"]:
        raise HTTPException(status_code=401, detail="Did delete token")
    return bool_token