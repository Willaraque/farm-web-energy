from Librerias.lib import *
from Librerias.vars import *
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt 
import os #jwt
from passlib.context import CryptContext
from typing import Annotated


# ----------------- Manejo de exceptions -----------
def HTTPExceptions():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#--------------- Generación de Tokens --------------

def create_access_token(data: dict, expires_delta: Union[datetime, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=str(os.getenv('ACCESS_TOKEN_SECRET')), algorithm=str(os.getenv('ALGORITHM')))
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=str(os.getenv('REFRESH_TOKEN_SECRET')), algorithm=str(os.getenv('ALGORITHM')))
    return encoded_jwt

#-------------- Llamar a la base de datos ------------
async def get_user(username):
    user_data = await db_user.find_one({'username': username})
    if user_data: 
        return UserInDB(**user_data)
    else: 
        return []

async def verify_password(plane_password:str, hashed_password:str):
    context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=50000
    )
    is_valid = context.verify(plane_password, hashed_password)
    return is_valid

async def authenticate_user(username, password):
    user = await get_user(username)
    if not user:   
        raise HTTPExceptions()
    if not await verify_password(password, user.password):
        raise HTTPExceptions()
    return user

#-------------- Guardar los token en base de datos y eliminarlos ----------------------
async def save_token(_idUser:str, username:str, dict_jwt:dict):
    object_id = ObjectId(_idUser)
    infos = {'_id': _idUser, 'username':username,  **dict_jwt}
    existe = await db_token.find_one({'_id': object_id}) #is not None
    if existe:
        dict_to_upload = deepcopy(infos)
        saveToken = db_token.replace_one(infos, dict_to_upload)
    else:
        saveToken = await db_token.insert_one(infos)

    create_token = await db_token.find_one({'_id': object_id})
    create_token['_id'] = str(create_token['_id'])
    return create_token

async def update_token(refreshToken:str, dict_jwt:dict):
    existe = await db_token.find_one({'access_token': str(refreshToken)}) #is not None
    if existe:
        newvalues = { "$set": dict_jwt }
        saveToken = db_token.update_one({'access_token': str(refreshToken)}, newvalues)
    refresh_token = await db_token.find_one({'access_token': str(dict_jwt['access_token'])})
    refresh_token['_id'] = str(refresh_token['_id'])
    return refresh_token

async def get_token(_idUser:str, refreshToken:str):
    infos = {'_id': ObjectId(_idUser),'refresh_token':refreshToken}
    document_token = await db_token.find_one(infos)
    document_token['_id'] = str(document_token['_id'])
    if document_token: 
        return document_token
    return None

#--------------- Dependencias para saber que estoy loggeado ---- --------------

async def get_user_current(token: Annotated[str,Depends(oauth2_scheme)]) -> dict:
    try:
        payload = jwt.decode(token, key=str(os.getenv('ACCESS_TOKEN_SECRET')), algorithms=[str(os.getenv('ALGORITHM'))])
        username: str = payload.get("sub")
        if username is None: 
            raise HTTPExceptions()
    except jwt.PyJWTError:
        raise HTTPExceptions()
    users = await get_user(username)
    if not users:
        raise HTTPExceptions()
    return users


async def get_user_active_current(user: User = Depends(get_user_current)):
    if not user.active:
        raise HTTPException(status_code=400, detail="Usario Inactivo")
    return user


#-------------- Verificación del Token (verify-token) ----------

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, key=str(os.getenv('ACCESS_TOKEN_SECRET')), algorithms=[str(os.getenv('ALGORITHM'))])
        return {"valid": True}
    except jwt.PyJWTError:
        return {"valid": False}
    
async def verify_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, key=str(os.getenv('ACCESS_TOKEN_SECRET')), algorithms=[str(os.getenv('ALGORITHM'))])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    

async def drop_tokenBD(id:str):
    try:
        objet_id = ObjectId(id)
        existe = await db_token.find_one({'_id':objet_id}) #is not None
        if existe:
            saveToken = await db_token.delete_one({'_id':objet_id})
            return {"valid": True}
        else: return {"valid": False}
    except:
        return {"valid": False}


