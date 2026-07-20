# farm-web-energy
web energy, fastpai, mongo, react 

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
