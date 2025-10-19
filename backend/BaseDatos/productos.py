from Librerias.lib import *
from Librerias.vars import *

#-------------- Creando los productos ------------------
async def get_one_task_id(id):
    task = await db_products.find_one({'_id':ObjectId(id)})
    task['_id'] = str(task['_id'])
    return task

async def get_one_task(name):
    task = await db_products.find_one({'name':name})
    return task

async def get_all_tasks():
    tasks = []
    cursor = db_products.find({})
    async for document in cursor:
        document['_id'] = str(document['_id'])
        tasks.append(Task(**document))
    return tasks

async def create_one_task(task):
    new_task = await db_products.insert_one(task)
    create_task = await db_products.find_one({'_id': new_task.inserted_id})
    return create_task

async def update_task(id:str, data):
    task = {key:value for key, value in data.dict().items() if value is not None}
    # print(task)
    await db_products.update_one({'_id':ObjectId(id)}, {'$set':task})
    document = await db_products.find_one({'_id': ObjectId(id)})
    return document

async def delete_one_task(id:str):
    await db_products.delete_one({'_id':ObjectId(id)})
    return True