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
    markets, countrys = ['PBC','PIB','INTRA'], ['español']#'portugues' 

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

    def __cleaningData__(cls, result)->pd.DataFrame:
        result = result.apply(lambda x: x.str.strip().str.replace('.', ','), axis=1).rename(columns={0:'header'})
        result = result.dropna(how='all', axis=1).dropna(how='all', axis=0).fillna('')
        return result

    def __headers__(cls, headers):
        headers = headers.replace('', np.nan).dropna(axis=1, how='all')
        columns = ['Fichero', 'Emision', 'Fecha', 'Tipo']
        if len(headers.columns) == len(columns): headers.columns = columns
        index  = headers.T.index.tolist()
        values = headers.T[0].values.tolist()
        headers = pd.Series(values, index=index)
        extractall_date = next(iter(re.findall(r'(?i)\d{0,2}[/]\d{0,2}[/]\d{0,4}', headers['Fecha'])))
        headers['Fecha'] = FormatDate(date= extractall_date).date.strftime('%Y-%m-%d')
        return headers
    
    def __requesToData__(cls, request)->pd.DataFrame:
        result = pd.DataFrame()
        file = [i for i in request.text.replace('\r','').split('\n') if i != '']
        if bool(file):
            for idx in file:
                result = pd.concat([result, pd.Series([idx]).str.split(';', expand=True)],axis=0, join='outer').replace('', np.nan).fillna(np.nan).reset_index(drop=True)
        elif cls.warning: raise ValueError('I haven`t information for extractall of requests')
        return result
    
    def __ApplyDateSeason__(cls, infos, data, sesion):
        #Date-Hours, with Change Hours
        date = data.filter(regex=r'(?i).*(date|fec|ho).*', axis=0)
        if not date.empty or isinstance(date, str): date = FormatDate(date= date.Date).date.to_pydatetime()
        elif infos['header'] != None or  not infos['header'].empty: date = FormatDate(date= next(iter(infos['header']['Fecha'])))
        elif cls.warning: raise ValueError('I haven`t date for append to Date')

        #---------- Apply Data and Season---------------
        desde, hasta = deepcopy(date).replace(hour=0), deepcopy(date).replace(hour=23)
        if sesion !=None and sesion ==2:desde = (date - timedelta(days=1)).replace(hour=20)
        Date = FormatDate.Añadir_cambios_horarios(start = desde, end=hasta, freq='H')
        Date.insert(Date.columns.size, 'Hour', Date['Date'].dt.hour)
        return Date
    
    def __transformingData__(cls, table, infos:dict={}, continuo:bool=False, report:bool=False):
        if report:
            table = table.drop(columns=infos.get('groupby'), errors='ignore').reset_index(drop=True)
            table = table.T.reset_index(names='Hour').rename(columns={0:infos.get('group')})
            table.Hour = table.Hour.astype(int) -1
            table = pd.merge(infos.get('Date'), table, how='left', on='Hour')
            if table[infos.get('date_groupby')].duplicated().any(): table = table.drop_duplicates(subset=infos.get('date_groupby'), keep='first')
        elif continuo:
            headers = table[table['header'].str.match(r'(?i).*fecha.*')]
            table = table.drop(index = headers.index, errors='ignore')
            table.columns = headers.values[0].tolist()
            table = table.drop(columns=['Fecha'], errors='ignore').rename(columns={'Contrato':'Hour'})
            table.Hour = table.Hour.astype(int) -1
            table = pd.merge(infos.get('Date'), table, how='left', on='Hour').fillna('0,0')
        else:
            table.loc[table.header == '', 'header'] = 'Hour'
            reindex_columns = table[table['header'].str.match(r'(?i).*hour.*')]
            table = table.drop(index=reindex_columns.index, errors='ignore')
            table.columns = reindex_columns.values[0].tolist()
            table = table.replace('', np.nan).dropna(how='all', axis=1)
        return table
      
    @staticmethod
    def __extractallData__(cls:Callable[..., Any], 
                                infos:pd.Series=...,
                                data:pd.Series=...,
                                request:bool=...,
                                sesion:int=None) ->dict:
        
        infos.update({'header':None, 'data':None})
        result = PrecioOMIE.__requesToData__(cls, request)
        if not result.empty:
            #----------------- Cleaning of Data --------------
            result = PrecioOMIE.__cleaningData__(cls, result)

            #------- Extractall of headers-------
            mask_headers = result['header'].str.match(r'(?i).*(?:omie|mercado(\\s)de(\\s)elec).*')
            headers = result[mask_headers]
            if not headers.empty:  infos.update({'header':PrecioOMIE.__headers__(cls,headers)})
            elif cls.warning: raise ValueError(f'I haven`t headers the document')

            #---------  Date-Hours, with Apply Data and Season ---------------
            Date = PrecioOMIE.__ApplyDateSeason__(cls, infos=infos, data=data, sesion=sesion)
            date_groupby = ['Date', 'Season','Hour']
            infos.update({'date_groupby':date_groupby, 'Date':Date})
            

            #Also negation of headers, is infos of price: Spain, Portugal 
            list_data = []
            table = result[~mask_headers]
            if not bool(re.findall(r'(?i).*intra.*', infos.get('market'))):
                table = PrecioOMIE.__transformingData__(cls, table=table)
                #----------- Multiply data, forms for save in BBDD -----------
                infos.update({'groupby':table.filter(regex=r'(?i).*^((?!\d+).)*$',axis=1).columns.tolist()})
                for group, df in table.groupby(infos.get('groupby')):
                    infos.update({'group':group})
                    list_data.append(PrecioOMIE.__transformingData__(cls, table=df, infos=infos, report=True))
            else: list_data.append(PrecioOMIE.__transformingData__(cls, table=table, infos=infos, continuo=True)) #Market Continuo

            if bool(list_data):
                data = functools.reduce(lambda l,r: pd.merge(l, r, how='outer', on=date_groupby), list_data)
                data = data.drop(columns=['Hour'], errors='ignore')
                if not data.empty: infos.update({'data':data})
            elif cls.warning: raise ValueError('The list of Data is empty')

        elif cls.warning: raise ValueError('I haven`t information about of request to Api Public OMIE')
        return infos
    

    @staticmethod
    def decorator_Market(fuctions):
        def wraps(*args, **kwargs):
            if len(args)==3: return fuctions(*args, **kwargs)
            else: raise ValueError(F'El decorador de Market falla, debido a los argumentos que recibe')
        return wraps 

    def __inputs__(cls, data):
        #--------- Inputs for Search document in API in OMIE -------------
        market = next(iter(data.filter(regex=r'(?i).*merca.*', axis=0)))
        date = next(iter(data.filter(regex=r'(?i).*date.*', axis=0)))
        if isinstance(date, str): date = FormatDate(date=date).date
        year, month, day, market = date.year, str(date.month).zfill(2), str(date.day).zfill(2), market 

        #----------- URL for POST API OMIE -------------
        website_one = f'https://www.omie.es/sites/default/files/dados/AGNO_{year}/MES_{month}/TXT'
        infos = {'bool_intra':bool(re.findall(r'(?i).*pib.*', market)), 
                 'bool_continuo':bool(re.findall(r'(?i).*intra.*', market)), 
                 'year':year, 'month':month, 'day':day, 'market':market}
        return  website_one, infos

    def __wbsaiteApi__(cls, website_one,
                       infos, sesion):
        year, month, day, market = infos.get('year'), infos.get('month'), infos.get('day'), infos.get('market')
        if infos.get('bool_intra'): website_two = f'/INT_{market}_EV_H_1_{sesion}_{day}_{month}_{year}_{day}_{month}_{year}.TXT'
        elif infos.get('bool_continuo'): website_two = f'/INT_{market}_C_MIN_MAX_1_{day}_{month}_{year}_{day}_{month}_{year}.TXT'
        else: website_two = f'/INT_{market}_EV_H_1_{day}_{month}_{year}_{day}_{month}_{year}.TXT'
        return  website_one + website_two

    def __uploadMongoDB__(cls, infos:dict, sesion:int):
        market, year, month, day = infos.get('market'), infos.get('year'), infos.get('month'), infos.get('day')
        df = infos.get('data')
        df.Date = df.Date.dt.strftime('%Y-%m-%dT%H:00:00')
        #------ Filter searching in BBDD -------
        filter = infos['header'].to_dict()
        if not mongo['Proyecto_Baterias']['OMIE'].count_documents(filter):
            filter.update({'Datos':df.to_dict(orient='records')})
            mongo['Proyecto_Baterias']['OMIE'].insert_one(filter)
            if cls.print: print(f"{datetime.now()} Insert one document in Market: {market}- Sesion: {sesion}, Date: {year}-{month}-{day}")
        else:
            dict_upload = deepcopy(filter)
            dict_upload.update({'Datos':df.to_dict(orient='records')})
            mongo['Proyecto_Baterias']['OMIE'].replace_one(filter, dict_upload)
            if cls.print: print(f"{datetime.now()} Replace one document in Market: {market}- Sesion: {sesion}, Date: {year}-{month}-{day}")
    
    @staticmethod
    def __treatmentFile__(cls, data:pd.Series) ->pd.Series:
        website_one, infos  = PrecioOMIE.__inputs__(cls, data)
        end_run = 7 if infos.get('bool_intra') else 2
        for secc in range(1, end_run):
            request = DataUtils.__request__(cls, PrecioOMIE.__wbsaiteApi__(cls, website_one, infos,  sesion=secc))
            if bool(request) and request.status_code == 200 and not data.empty:
                infos = PrecioOMIE.__extractallData__(cls, infos=infos, data=data, request=request, sesion=secc)
                if bool(infos): PrecioOMIE.__uploadMongoDB__(cls, infos=infos, sesion=secc)
                elif cls.warning: raise ValueError('The extractallData failed')
            # elif cls.warning: raise ValueError('There are not files in the API -> OMIE')  

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
        Market = DataUtils.__combinations__(cls, dates)
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
        expr_regu = f'(?i).*Fecha|Season|tipo|precio margi.*españ.*'
        begin, ends = cls.desde.strftime('%Y-%m-%d'), cls.hasta.strftime('%Y-%m-%d')
        if bool(cls.kwargs): 
            market = pd.DataFrame(cls.kwargs).filter(regex='(?i).*merca|marke.*', axis=1)
            if not market.empty: market = '|'.join(pd.Series(market.apply(lambda x: x.values, axis=1)).explode().tolist())
        else: market = 'diario|intra'
        # print(market, begin, ends)
        pipeline = [{'$match':{'Tipo':{'$regex':f'(?i).*{market}.*', '$options':'i'},
                               '$and':[{'Fecha':{'$gte':begin}},{'Fecha':{'$lte':ends}}]}},
                    {'$unwind':'$Datos'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
                    {'$set':{'Fecha':{'$toDate':'$Date'},'Season':{'$toDouble':'$Season'} }},
                    {'$project':{'_id':0, 'Fichero':0, 'Emision':0, 'Datos':0, 'Date':0}}]
        conexion = cls.mongo
        cursor = conexion['ENERGIA']['Precios Omie'].aggregate(pipeline, allowDiskUse=True)
        result_list = await cursor.to_list(length=None)
        print(result_list)
        result = pd.DataFrame(result_list)
        # result = pd.DataFrame(cls.mongo.Proyecto_Baterias.OMIE.aggregate(pipeline, allowDiskUse=True))
        if not result.empty:
            result = result.filter(regex=expr_regu, axis=1)
            rename_colums = result.filter(regex='(?i).*precio margi.*españ*', axis=1).columns.tolist()
            result = result.rename(columns = {i:'Precio Español'  for i in rename_colums if bool(re.match('(?i).*sistema español.*', i))})
            if  ('Tipo' and 'Precio Español') in result.keys().tolist(): 
                result['Tipo'] = result['Tipo'].str.replace('Precio del mercado', '', regex=True).str.replace(' ', '', regex=True).str.replace('[(]EUR/MWh[)]', '', regex=True)
                result['Precio Español'] = result['Precio Español'].str.replace(',', '.').apply(pd.to_numeric)
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
            result = result[~(isnan&isnull)].sort_values(by=['Tipo', 'Fecha']).reset_index(drop=True)
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
