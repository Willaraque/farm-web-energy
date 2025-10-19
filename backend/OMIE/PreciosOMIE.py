try:
    from Librerias.lib import *
    from Librerias.vars import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)
    from Librerias.lib import *

from Utilities.Comprobaciones_horarias import *

class PrecioOMIE:
    '''@staticmethod -> Method for acceder since the class
       @classmethod  -> Method for don't arguments the class
       @property     -> Method for do calculate inside'''
    mongo = mongoDB.connect_db(host='wac')  
    args, kwargs = (), {}
    markets = {'Mercado':['diario','intradiario','continuo'], 'Archivo':['marginalpdbc_','marginalpibc_','precios_pibcic_']}


    @staticmethod
    def __decorator_kwargs__(fuction):
        @functools.wraps(fuction) #wraps es un decorador de decoradores para traer los comentarios
        def wrappers(*args, **kwargs):
            self_input = list(args)
            for value in self_input:
                if isinstance(value, dict|tuple|type):
                    if not isinstance(value, type) and len(value)>0: 
                        return fuction(*args, **kwargs)
        return wrappers

    @__decorator_kwargs__
    def __extractall_kwargs__(self, *args, **kwargs):
        '''Estamos extrayendo los kwargs y args de la clase OMIE'''
        if len(args)>0:
            for idx in list(args): 
                if isinstance(idx, dict) and len(idx)>0: 
                    for key, val in idx.items(): 
                        self.kwargs.update({key:[str(i).strip().lower() for i in val] if isinstance(val,list) else str(val).strip().lower()})
                else: self.args += idx
        return self


    def __init__(self, *args, **kwargs) -> None:
        self.mongo = mongo
        self.args = args
        self.kwargs = kwargs

    def __cleaningData__(cls:Callable[..., Any]
                         ,data)->pd.DataFrame:
        #--------- Limpieza y Tratamiento de datos --------
        data.Path = f"{data.Path}/{data.Archivo}"
        sesion = int(data.Archivo.split('.')[0][-1]) if data.Mercado.startswith('intra') else 0
        if sesion > 0: data.Mercado = f"{data.Mercado} {sesion}" 
        boolmarket = data.Mercado.startswith('cont')
        if boolmarket: 
            df = pd.read_csv(data.Path, sep=';', skiprows=2, engine='python', skipfooter=1, encoding='ansi', on_bad_lines='skip')
            df = df.filter(regex='(?i).*^((?!añ|mes|d|hor).)*$', axis=1)
        else: df = pd.read_csv(data.Path, sep=';').reset_index()

        #-------- Eliminamos las columnas que comiencen por Unnamed --------
        try: columnsDrop = next(iter(df.filter(regex='(?i).*unn.*', axis=1).columns))
        except: columnsDrop = ''
        if bool(columnsDrop): df = df.drop(columns=[columnsDrop], errors='ignore').dropna(axis=0)
        if len(df)>1: df = df.applymap(lambda x: float(str(x).replace('.', '').replace(',', '.')) if data.Mercado.startswith('con') else float(str(x).replace(',', '.')))
        if not boolmarket: df = df.rename(columns = {col: f'Precio {newcol}' for col, newcol in zip(df[df.columns[-2:]].columns, ['Portugues','Español'])})
        return df, data
    
    def __ApplyDateSeason__(cls, infos, data):
        #Date-Hours, with Change Hours
        date = infos.filter(regex=r'(?i).*(date|fec|ho).*', axis=0)
        if not date.empty or isinstance(date.Fecha, str): date = FormatDate(date= date.Fecha).date
        elif cls.warning: raise ValueError('I haven`t date for append to Date')

        #---------- Apply Data and Season---------------
        desde, hasta = deepcopy(date).replace(hour=0), deepcopy(date).replace(hour=23)
        bool_intra, bool_date = infos.Mercado.startswith('intra'), date <= datetime(2024,6,13)
        if bool_intra:
            if bool_date:
                if infos.Mercado[-1] =='1': 
                    if date <= datetime(2019,11,12): desde = (date - timedelta(days=1)).replace(hour=21)
                elif infos.Mercado[-1] =='2': 
                    if date > datetime(2019,11,12): desde = (date - timedelta(days=1)).replace(hour=20)
                elif infos.Mercado[-1] =='3': 
                     if date <= datetime(2019,11,12):  desde = date.replace(hour=4)
                elif infos.Mercado[-1] =='4': 
                    if date <= datetime(2019,11,12): desde = date.replace(hour=7)
                    else: desde = date.replace(hour=4)
                elif infos.Mercado[-1] =='5': 
                    if date <= datetime(2019,11,12): desde = date.replace(hour=11)
                    else: desde = date.replace(hour=7)
                elif infos.Mercado[-1] =='6': 
                    if date <= datetime(2019,11,12): desde = date.replace(hour=15)
                    else: desde = date.replace(hour=12)
            elif infos.Mercado[-1] =='3': 
                desde = date.replace(hour=12)
        Date = FormatDate.Añadir_cambios_horarios(start = desde, end=hasta, freq='H')

        #-----Juntamos los Dataframe por el index -------
        data.insert(data.columns.size, 'index', data.index)
        Date.insert(Date.columns.size, 'index', Date.index)
        data = Date.merge(data, how='inner', on=['index'])
        data = data.filter(regex='(?i).*^((?!Fe|in|lev).)*$', axis=1) #Filtramos para quedarnos con las columnas que necesitamos
        return data

    @staticmethod
    def decorator_Market(fuctions):
        def wraps(*args, **kwargs):
            if len(args)==3: return fuctions(*args, **kwargs)
            else: raise ValueError(F'El decorador de Market falla, debido a los argumentos que recibe')
        return wraps 

    def __searchingFile__(cls:Callable[..., Any], 
                          data:pd.Series):
        #--------- Inputs for Search -------------
        date, path = data.Fecha.strftime('%Y%m%d'), data.Path
        data.Fecha = data.Fecha.strftime('%Y-%m-%d')
        df_copy = deepcopy(data.to_frame().T)

        # Buscamos el archivo en la carpeta de descarga, del mismo proyecto
        df = pd.Series(os.listdir(path))
        bool_date = df.str.contains(f'(?i).*{date}.*', regex=True)
        data_df = df[bool_date].reset_index(drop=True)
        if not data_df.empty:
            df_copy = df_copy.filter(regex='(?i).*^((?!Arc).)*$', axis=1)
            df_copy = df_copy.merge(data_df.to_frame(name='Archivo'), how='cross')
            cols = list(df_copy.columns)
            cols.insert(3, cols.pop(-1))  # Sacar la última columna y colocarla en la posición 4
            df_copy = df_copy[cols]
        elif  data_df.empty: df_copy =  pd.DataFrame()
        elif cls.warning: raise ValueError(f'El archivo con la fecha: {date} no ha sido descargado') 
        return df_copy

    def __uploadMongoDB__(cls:Callable[..., Any],
                          infos:dict):
        #------- Extraemos la data -----------
        df = infos.get('Data')
        df.Date = df.Date.dt.strftime('%Y-%m-%dT%H:00:00')
        infos.pop('Data') #Eliminamos y actualizamos el diccionario
        #------ Filter searching in BBDD -------
        filter = deepcopy(infos)
        mongo = cls.mongo
        if not mongo['ENERGIA']['Precios Omie'].count_documents(filter):
        # if not mongo['Proyecto_Baterias']['omie_test'].count_documents(filter):
            filter.update({'Datos':df.to_dict(orient='records')})
            # mongo['Proyecto_Baterias']['omie_test'].insert_one(filter)
            mongo['ENERGIA']['Precios Omie'].insert_one(filter)
            if cls.print: print(f"{datetime.now()} Insert one document in Market: {infos.get('Mercado')}, Date: {infos.get('Fecha')}")
        else:
            dict_upload = deepcopy(filter)
            dict_upload.update({'Datos':df.to_dict(orient='records')})
            # mongo['Proyecto_Baterias']['omie_test'].replace_one(filter, dict_upload)
            mongo['ENERGIA']['Precios Omie'].replace_one(filter, dict_upload)
            if cls.print: print(f"{datetime.now()} Replace one document in Market: {infos.get('Mercado')}, Date: {infos.get('Fecha')}")

    @staticmethod
    def __extractallData__(cls:Callable[..., Any],
                           infos):

        result, infos = PrecioOMIE.__cleaningData__(cls, data=infos)
        if not result.empty and len(result)>1:
            result = PrecioOMIE.__ApplyDateSeason__(cls, infos=infos, data=result)
            infos = infos.filter(regex='(?i).*^((?!añ|pat).)*$', axis=0).to_dict()
            infos.update({'Data':result})
            if bool(infos): PrecioOMIE.__uploadMongoDB__(cls, infos=infos)
        elif cls.warning: raise ValueError('The extractallData failed')

    @staticmethod
    def __treatmentFile__(cls, data:pd.Series) ->pd.Series:

        PrecioOMIE.__dowloadFiles__(cls, data=data)
        # Pensar en como pasarme el mercado como variable, porque en el intradiario, habrá una nueva columnas (donde vienen las secciones)
        results = PrecioOMIE.__searchingFile__(cls, data=data)
        if not results.empty:
            results.apply(lambda df: PrecioOMIE.__extractallData__(cls, infos=df), axis=1)
        elif cls.warning: raise ValueError('The extractallData failed')

    @staticmethod
    def __ComprobacionFile__(cls, data:list, path:str, year:int):

        # Comprobacion de archivos existentes, para no repetir descarga.
        filePageSplit = pd.Series(data).str.split('=', expand=True)
        filePageSplit = filePageSplit[filePageSplit.columns[-1]]
        filePageSplit = filePageSplit[filePageSplit.str.contains(f'(?i).*{year}.*', regex=True)].reset_index(drop=True)
        fileExists = pd.Series(os.listdir(path))
        FileNew = filePageSplit[~filePageSplit.isin(fileExists)]

        if not FileNew.empty:
            filePage, links_df = pd.Series(data), []
            for i in FileNew.index:
                file = next(iter(filePage[filePage.str.contains(FileNew[i])]))
                links_df.append(file)
            data = links_df
        else: data = []
        return data
    
    @staticmethod
    def __dowloadFiles__(cls, 
                         data:pd.Series) -> bool:
        # Extraccion de variables principales para la busqueda de informacion 
        año = next(iter(data.filter(regex='(?i).*añ.*', axis=0)))
        # market = next(iter(data.filter(regex='(?i).*merca.*', axis=0)))
        url = next(iter(data.filter(regex='(?i).*websi.*', axis=0)))
        # Descargar archivos desde los enlaces extraídos
        output_folder = data.Path
        [os.makedirs(i) for i in [output_folder] if not os.path.exists(i)] #Creamos el directorio de Descarga de los Zips
        #Este booleano esta pensado en si está un solo documento
        file = pd.Series(os.listdir(output_folder))
        regex_date = data.Fecha.strftime('%Y%m%d')
        file = file[file.str.contains(regex_date, regex=True)]
        if data.Mercado.startswith('con'):
            bool_len = True if data.Fecha.to_pydatetime() <= datetime(2018,6,13) else len(file) == 1 
        else: bool_len = len(file) == 1 if data.Mercado.startswith('di') else len(file) in [3,6]
        
        if not bool_len:
            response = requests.get(url) # Realizar la solicitud GET
            if response.status_code == 200:
                soup = bs(response.content, 'html.parser')
                # Localizar la tabla en el HTML
                table = soup.find('table', {'class': 'responsive-enabled'})
                # Extraer filas con hipervínculos, Busca la etiqueta <a> con el atributo href, Guarda el enlace
                links = [ row.find('a', href=True)['href'] for row in table.find('tbody').find_all('tr') if row.find('a', href=True) ] 
                links = PrecioOMIE.__ComprobacionFile__(cls, data=links, path=output_folder, year=año)
                if bool(links):
                    for link in links:
                        # Crear la URL completa si es relativa
                        file_url = requests.compat.urljoin(url, link)
                        filename = file_url.split('=')[-1]
                        filename = filename.replace('?', '_').replace('&', '_') 
                        file_path = os.path.join(output_folder, filename)
                        # Descargar el archivo
                        file_response = requests.get(file_url)
                        if file_response.status_code == 200:
                            with open(file_path, 'wb') as file:
                                file.write(file_response.content)
                                if cls.print: print(f"Archivo descargado: {filename}")
                        else:
                            if cls.print: print(f"Error al descargar {file_url}")
            else: 
                if cls.print: print(f"Error al acceder a la página. Código de estado: {response.status_code}")  
    

    @classmethod    
    def get_dowload_price(cls:Optional[type], 
                          start:str|datetime, 
                          end:str|datetime,
                          multiproccesing:bool=True,
                          print:bool = False,
                          warning:bool=False,
                          combinations:dict = None,
                          *args, **kwargs):
        
        #Arguments o Kwargs (extractall)
        cls.warning, cls.print = warning, print
        PrecioOMIE.__extractall_kwargs__(cls, args, kwargs)

        #Format of Date
        fomartdates = FormatDate(start=start, end=end)
        cls.start, cls.end = fomartdates.start, fomartdates.end 
        dates = FormatDate.Añadir_cambios_horarios(start = cls.start, end=cls.end, freq='D')
        Market = DataUtils.__combinations__(cls, range=dates)
        if not Market.empty: 
            '''Pensar como pasarle el Multiprocessing para que la subida de datos, sea rapida'''
            if bool(multiproccesing):
                Market['DataFrame'] = [pd.Series([dia,country, merca], index=['Date', 'country', 'mercado']) for dia, country, merca in 
                                       zip(Market.Date, Market.country, Market.mercado)]
                Market = Market.drop(columns=['Date', 'country', 'mercado'], errors='ignore')
                Market.insert(0, 'cls', cls)
                cores = int((mp.cpu_count()/2)+1) 
                Range = list(Market.itertuples(index=False, name=None)) 
                with Pool(cores) as pool:
                    print({f'INICIALIZAMOS EL MULTIPROCESSING CON {cores} CORES'.center(80,'-')})
                    pool.starmap(PrecioOMIE.__treatmentFile__, Range)
                    print({f'FIN DEL PROCESO'.center(80,'-')})
            else: Market.apply(lambda df: PrecioOMIE.__treatmentFile__(cls, data=df), axis=1)

    @staticmethod
    async def __extractall_precios__(cls, 
                               Date:Optional[pd.DataFrame]) -> Tuple[list,...]:
        #---------- Inputs ---------------
        expr_regu = f'(?i).*Fecha|Season|Mercado|precio .*españ.*'
        begin, ends = cls.desde.strftime('%Y-%m-%d'), cls.hasta.strftime('%Y-%m-%d')
        if bool(cls.kwargs): 
            market = pd.DataFrame(cls.kwargs).filter(regex='(?i).*merca|marke.*', axis=1)
            if not market.empty: market = '|'.join(pd.Series(market.apply(lambda x: x.values, axis=1)).explode().tolist())
        else: market = 'diario|intra'
        # print(market, begin, ends)
        pipeline = [{'$match':{'Mercado':{'$regex':f'(?i).*{market}.*', '$options':'i'},
                               '$and':[{'Fecha':{'$gte':begin}},{'Fecha':{'$lte':ends}}]}},
                    {'$unwind':'$Datos'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
                    {'$set':{'Fecha':{'$toDate':'$Date'},'Season':{'$toDouble':'$Season'} }},
                    {'$project':{'_id':0, 'Fichero':0, 'Emision':0, 'Datos':0, 'Date':0}}]
        conexion = cls.mongo
        # cursor = conexion['ENERGIA']['Precios Omie'].aggregate(pipeline, allowDiskUse=True)
        cursor = conexion['ENERGIA']['Precios Omie'].aggregate(pipeline, allowDiskUse=True)
        result_list = await cursor.to_list(length=None)
        print(result_list)
        result = pd.DataFrame(result_list)
        if not result.empty:
            result = result.filter(regex=expr_regu, axis=1)
            rename_colums = result.filter(regex='(?i).*precio .*españ*', axis=1).columns.tolist()
            result = result.rename(columns = {i:'Precio Español'  for i in rename_colums if bool(re.match('(?i).*español.*', i))})
        elif cls.warning: raise ValueError(f'Fallo la base de datos de OMIE -> MongoDB')
        return result

    @classmethod 
    async def get_precios(cls:Optional[type], desde:str|datetime, 
                          hasta:str|datetime,
                          warning:bool=False, 
                          *args, **kwargs) -> pd.DataFrame:
        result = pd.DataFrame()
        cls.warning = warning
        dates = FormatDate(start=desde, end=hasta)
        cls.desde, cls.hasta = dates.start, dates.end
        PrecioOMIE.__extractall_kwargs__(cls, args, kwargs)
        date_aux = pd.date_range(start=cls.desde.replace(hour=0), end=cls.hasta.replace(hour=23), 
                                 freq='D').to_frame(name='Date').reset_index(drop=True)
        date_aux = FormatDate.Añadir_cambios_horarios(start = cls.desde, end=cls.hasta.replace(hour=23), freq='H')
        result = await PrecioOMIE.__extractall_precios__(cls, date_aux)
        if not result.empty:
            #----Aqui quitamos los valores isnull and isna. Limpieza de datos
            isnan, isnull = result['Precio Español'].isna(), result['Precio Español'].isnull()
            result = result[~(isnan&isnull)].sort_values(by=['Mercado', 'Fecha']).reset_index(drop=True)
        elif cls.warning: raise ValueError('Fallo la base de datos de OMIE')
        return result



if __name__ == '__main__':
    '''Clase para Precios OMIE
        Inputs:
            -Desde:str|datetime
            -Hasta:str|datetime
            -multiprocessing:True or False
            -Combinations: str or list[str], depende del mercado a estudiar'''
    precios = PrecioOMIE.get_precios('2021-01-01','2024-05-01', 
                                    warning=False, mercado=['diario', 'intra']) #'continuo'
    print(precios)
    # omie = PrecioOMIE.get_dowload_price('2024-01-01','2024-02-23', 
    #                                     multiproccesing=False, warning=False)
