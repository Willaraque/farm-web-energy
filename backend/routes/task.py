from Librerias.lib import *
from Librerias.vars import *
from fastapi import APIRouter, HTTPException

'''
GET -> pide datos
POST -> crea datos
PUT -> Actualiza datos
DELETE -> Elimina datos 
CRUD -> Create, Read, Update, Delete 
'''

task = APIRouter()

@task.get('/api/tasks')
async def get_tasks():
    tasks = await get_all_tasks()
    return tasks

@task.post('/api/tasks', response_model=Task)
async def create_task(task: Task):
    taksFound = await get_one_task(task.name)
    if taksFound:     
        raise HTTPException(409, 'Task already exists')
    response = await create_one_task(task.dict())
    if response: 
        return response
    raise HTTPException(400, 'Something went wrong')

@task.get('/api/tasks/{id}', response_model=Task)
async def get_task(id:str):
    tasks = await get_one_task_id(id)
    if tasks:
        return tasks
    raise HTTPException(404, f"Task with id: {id} not found")


@task.put('/api/tasks/{id}', response_model=Task)
async def put_tasks(id:str, task: UpdateTask):
    response = await update_task(id, task)
    if response:
        return response
    raise HTTPException(404, f"Task with id: {id} not found")

@task.delete('/api/tasks/{id}')
async def remove_task(id:str):
    response = await delete_one_task(id)
    if response:
        return "Successfully deleted task"
    raise HTTPException(404, f"Task with id: {id} not found")

