try:
    from Librerias.lib import *
    from Librerias.vars import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)

from pcrenergy import (
    client_local,
    Omie,
    EsiosPlaywrightMongoScraper,
)
import re,os,sys
from fastapi import FastAPI, Form
from routes.task import task
from routes.users import app_users
from routes.tokens import app_tokens
from routes.prices import app_prices
from fastapi.middleware.cors import CORSMiddleware
from decouple import Config, RepositoryEnv


''' PARA CANCELAR EL SERVIDOR DE UVICORN O NODE.JS, utilizamos el comando CTROL + C'''
'''
                            BACKEND 
    Crear el entorno virtual, se ejecuta en la carpeta donde va a correr el servidor
    los comandos:

    - python -m venv fastapi-env  (Crea el entorno virtual)
    - fastapi-env\Scripts\activate (activar el fastapi)
    - pip install fastapi (Instalamos los modulos para utilizar fastapi)
    - pip install uvicorn
    - uvicorn main:app --reload (Para correr el servidor)
    
    Luego paramos el servidor de FASTAPI'''

'''
                            FRONTED
    Crear la carpeta y los frameworks que vamos a utilizar para hacer el front
    
    - Instalamos Node.js de la pagina oficial 
    - Luego, en variables de entorno, colocamos el path, donde quedo instalado Node.js y reiniciamos el equipo
    - utilizamos el comando -> npm create vite (ESTO ES LA TERMINAL, Pero en el poryecto de afuera)
    - Colocamos el nombre de la carpeta del front
    - Elegimos React y luego JavaScript
    - Luego damos click derecho en el explorador de visual code, y Seleccionamos Add Folder to Workspace
    - Installar los modulos utilizamos el comando -> npm i
    - Luego para ejecutar el proyecto del cliente -> npm run dev
    
    
    -Para crear dependencias de rutas, en el front es mucho mas facil por eso vamos a utilizar el comando
     -> npm i react-router-dom
    
    - npm i axios, instalar modulo para hacer llamados al codigo, limpiando el codigo, mucho mas sencillo '''

'''
                        CSS
    - Pagina tailwindcss -> para estilos de CSS (Es una biblioteca de utilidad)
    - Vamos a Get Start -> Framework guide -> seleccionamos el Vite, INSTALAMOS, npm install -D tailwindcss postcss autoprefixer, npx tailwindcss init -p
       (Debe primero parar el servidor, para hacer las respectivas instalaciones)
    - Instalar la extension Tailwind CSS IntelliSence -> sirve para el autocompletad

'''

app = FastAPI()

# print(config(str(os.getenv('FRONTED_URL'))))

config = Config(RepositoryEnv('.env'))
origins=[
    config('FRONTED_URL')
    # "http://13.38.10.75:5173"
]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, # Permite todos los orígenes, aunque en producción deberías limitarlo a los orígenes específicos de tu frontend
    allow_credentials=True,
    allow_methods=['*'], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=['*'], # Permite todos los encabezados
)

@app.get('/')
def welcome():
    return {'message': 'Welcome to the my FastAPI WILL!'}

app.include_router(task)
app.include_router(app_users)
app.include_router(app_tokens)
app.include_router(app_prices)




