from Librerias.lib import *
from Librerias.vars import *
from fastapi import APIRouter, HTTPException

'''
    #GET -> pide datos
    #POST -> crea datos
    #PUT -> Actualiza datos
    #DELETE -> Elimina datos 
    
'''

app_users = APIRouter()


@app_users.post('/api/users/create', response_model=CreateUser)
async def create_user(client: CreateUser):
    for key, value in vars(client).items():
        if not callable(value) and not key.startswith('__') and not isinstance(value, bool): setattr(client, key, str(value).strip())
    UserFound = await get_one_user(client)
    if UserFound:
        raise HTTPException(status_code=400, detail='El usuario ya existe')
    else:
        response = await create_one_user(client.dict())
        if response:
            return response
        raise HTTPException(status_code=409, detail='Something went wrong')
   

@app_users.post('/api/users', response_model=List[CreateUser])
async def get_users(client: UpdateUser = None):
    if client is not None and client.user is not None:
        response = await get_one_user(client)
        return [response]
    else:
        response = await get_all_users()
        return response   

@app_users.get('/api/users/{id}', response_model=CreateUser)
async def get_user(id:str):
    tasks = await get_one_user_id(id)
    if tasks:
        return tasks
    raise HTTPException(404, f"Task with id: {id} not found")

@app_users.put('/api/users/update/{id}', response_model=CreateUser)
async def put_users(id:str, client: UpdateUser):
    response = await update_user(id, client)
    if response:
        return response
    raise HTTPException(404, f"Task with id: {id} not found")

@app_users.delete('/api/users/delete/{id}')
async def remove_user(id:str):
    response = await delete_user(id)
    if response:
        return "Successfully deleted task"
    raise HTTPException(404, f"Task with id: {id} not found")

