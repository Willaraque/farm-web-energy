from Librerias.lib import *
from Librerias.vars import *

#-------------- Escriptando la contraseña -------------------------
def encriptar_password(password:str):
    # create CryptContext object
    context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=50000
    )
    # hash password
    hashed_password = context.hash(password)
    # Verify correct work
    is_valid = context.verify(password, hashed_password)
    if is_valid: password = deepcopy(hashed_password)
    return password

#---------------- Creando Usuarios para los persmisos y Login  -------------
async def create_one_user(USER):
    if USER['username'] != '' or USER['password'] != '':
        USER['password'] = encriptar_password(USER['password'])
        new_task = await db_user.insert_one(USER)
        create_user = await db_user.find_one({'_id': new_task.inserted_id})
        return create_user
    

async def get_one_user(client):
    username = client.username 
    password = encriptar_password(client.password)
    resp = await db_user.find_one({'$or':[{'username': username},{'password':password}]})
    return resp

async def get_all_users():
    users = []
    cursor = db_user.find({})
    async for document in cursor: 
        users.append(CreateUser(**document))
    return users

async def get_one_user_id(id):
    task = await db_user.find_one({'_id':ObjectId(id)})
    return task

async def update_user(id:str, data):
    user = {key:value for key, value in data.dict().items() if value is not None}
    await db_user.update_one({'_id':ObjectId(id)}, {'$set':user})
    document = await db_user.find_one({'_id': ObjectId(id)})
    return document

async def delete_user(id:str):
    await db_user.delete_one({'_id':ObjectId(id)})
    return True