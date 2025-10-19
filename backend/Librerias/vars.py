from Librerias.lib import *
from motor.motor_asyncio import AsyncIOMotorClient
from Utilities.db_connection import mongoDB


'''CONEXION CON LA BASE DE DATOS MONGO '''
mongo = mongoDB.connect_db()
# mongo_tera = mongoDB.connect_db('tera')

'''COLECCIONES A UTILIZAR '''
db_omie = mongo.Proyecto_Baterias.OMIE
db_products = mongo.PRODUCTOS.Productos
db_user = mongo.USERS.Users
db_token = mongo.USERS.Token
