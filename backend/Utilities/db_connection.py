from Librerias.lib import *
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

class mongoDB:

    def connect_db(host:str = ''):
        """
        CONEXION A MONGODB\n
            BY DEFAULT -> CONNECT TO LOCALHOST MONGODB DATABASE \n
        """
        mongo_username = ""
        mongo_password = ""
        if host.lower() == '':
            ssh_address = ""
            client = AsyncIOMotorClient("mongodb://" + mongo_username + ":" + mongo_password + "@" + ssh_address)
        elif 'test' in host.lower():
            ssh_address = "13.38.10.75"
            client = AsyncIOMotorClient("mongodb://" + mongo_username + ":" + mongo_password + "@" + ssh_address)
        else:
            client = AsyncIOMotorClient(os.getenv('DB_CONNECTION_STRING')) #AsyncIOMotorClient("mongodb://localhost:27017/")
        return client
    
    def __init__(self, host:str='') -> None:
        self.host = host 
    


