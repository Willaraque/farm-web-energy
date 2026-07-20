from Librerias.lib import *
from motor.motor_asyncio import AsyncIOMotorClient
from pcrenergy import client_local


'''CONEXION CON LA BASE DE DATOS MONGO '''
mongo = client_local()

'''COLECCIONES A UTILIZAR '''
db_omie = mongo.Proyecto_Baterias.OMIE
db_products = mongo.PRODUCTOS.Productos
db_user = mongo.USERS.Users
db_token = mongo.USERS.Token
