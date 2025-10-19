try:
    from Librerias.lib import *
    from Librerias.vars import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)
    from Librerias.lib import *
    from Librerias.vars  import *

class REE:

    @staticmethod
    def myfunc(columns:str, dict_index:dict={}) -> str:
        '''Functions for reiindex of columns'''
        dict_index = {'Fecha':'0', 'Hora':'0', 'Season':'1', 'UPR':'2', 
                      'Region':'3', 'Cierre':'4', 'Segmento':'5', 'Energia':'6', 'Precio':'7'}
        for key, val in dict_index.items():
            if columns in [key]: return val+columns
        else: return columns

    @staticmethod
    def __decorator_kwargs__(fuction):
        @functools.wraps(fuction) #wraps es un decorador de decoradores para traer los comentarios
        def wrappers(*args, **kwargs):
            self_input = list(args[1:])
            for value in self_input:
                if isinstance(value, dict) or isinstance(value, tuple) and bool(value): #isinstance(value, dict|tuple)
                    return fuction(*args, **kwargs)
        return wrappers

    @__decorator_kwargs__
    def __extractall_kwargs__(self, *args, **kwargs):
        '''Estamos extrayendo los kwargs y args de la clase OMIE'''
        for value in list(args): 
            if isinstance(value, dict) and bool(value): 
                self.kwargs = value
                # name = next(iter(value.keys()))
                # self.kwargs = value.get(name)
            else: 
                self.args = value
        return self

    @staticmethod
    def __checkout_sistema__(self, sistema:str=None) -> dict:
        dic_result = {}
        search = {'comercializadora':{'$regex':f'(?i).*^{self.comer}.*', '$options':'i'}}
        projection = {'_id':0} if sistema == None else {'_id':0, 'upr':1}
        dicts = pd.DataFrame(self.mongo_tera['Compra_Energia']['Codigos_Comerciales'].find(search, projection))
        if not dicts.empty:
            dic_result = deepcopy(dicts.to_dict(orient='records'))
        elif self.PrintWarning: raise ValueError(f'No se encontró region para la comer: {self.comer}, en la bbdd CodigosComerciales')
        return dic_result

    @staticmethod
    def __checkout_comer__(self, comer:str) -> bool:
        series = pd.Series(self.mongo_tera['Compra_Energia']['Codigos_Comerciales'].distinct('codecom'))
        return series.str.contains(f'(?i).*{comer.upper()}.*').any()
    
    @staticmethod
    def __change_upr__(self, upr:str)->str:
        search = {'upr':{'$regex':f'(?i).*^{upr}.*', '$options':'i'}}
        series = pd.Series(self.mongo_tera['Compra_Energia']['Codigos_Comerciales'].find_one(search, {'_id':0}))
        if not series.empty: series = next(iter(series.filter(regex=r'(?i).*codecom.*',axis=0)))
        elif self.PrintWarning: raise ValueError(f'No se encontró la UPR: {upr}, en la bbdd CodigosComerciales')
        return series

    def __init__(self, comer:str, PrintWarning:bool = True, #str|list
                 sistema:str=None, group:str='all',
                *args, **kwargs) -> None:
        
        self.mongo_tera = mongo_tera
        self.mongo_local = mongo_local
        if REE.__checkout_comer__(self, comer): self.comer = comer
        else: raise ValueError(f'La comercializadora, {comer} , no se encuentra en la base de datos[Codigos_Comerciales]')
        self.Infos = REE.__checkout_sistema__(self, sistema)
        if isinstance(self.Infos, dict) and len(self.Infos)>0:
            if 'comercializadora' in self.Infos.keys(): self.comer = self.Infos.get('comercializadora') 
        self.PrintWarning = PrintWarning
        self.group = group
        self.args = args
        self.kwargs = kwargs
        self = REE.__extractall_kwargs__(self, args, kwargs)

    def get_vert(self, date, fichero:str='VERT', 
                 TNP:bool=False, *args, **kwargs) -> pd.DataFrame: #str|datetime
        
        result = pd.DataFrame()
        #------ Inputs for search in BBDD CCH -> SIMEL --------
        if bool(kwargs): headers = '|^'.join(next(iter(pd.Series(kwargs).filter(regex='(?i).*colum.*', axis=0).values)))
        if isinstance(headers, list) and bool(headers): headers = '|'.join(headers)
        if isinstance(date, str): date = fecha_to_datetime(date)
        date = date.strftime('%Y-%m')
        if bool(self.Infos):
            Infos, region = pd.DataFrame(self.Infos), self.kwargs.get('Region')
            if region !=None: Infos = Infos[Infos['region'].str.contains(f'(?i).*{region}.*', regex=True)]
            if not Infos.empty: 
                expr_upr, code_ree = Infos['upr'].tolist(), Infos['coderee'].unique().tolist()
                region = [i.capitalize() for i in Infos['region'].unique().tolist()]

        #-------- Agrupamiento -----------
        group = {'Periodo de datos': '$Periodo de datos','Region':'$Region', 'UP': '$UP', 'Participante':'$Participante'}
        numero_de_unwind, array_for_project, list_cierres = 2, '$UltimosDatos', ['H2','H3','HP', 'HC']
        cases = [{'case':{'$eq':['$Periodo de cierre', tipo]}, 'then':index+1} for tipo, index in zip(list_cierres, range(len(list_cierres)))]
  
        pipeline = [{'$match':{'Fichero':{'$regex':fichero, '$options':'i'},
                                       'Region':{'$in':region},
                                        'Periodo de datos':{'$regex':date, '$options':'i'},
                                        'Participante':{'$in':code_ree},'UP':{'$in':expr_upr}}},
        
                    {'$set': {'Cierre': {'$switch': {'branches': cases, 'default':0}},
                      'Version': {'$toInt': '$Version'}}},
                    # Agrupamos por dia y filtramos los documentos para tener el ultimo fichero del ultiom cierre y ultima version 
                    {'$group':{'_id': group, 'UltimosDatos': {'$push':'$$ROOT'}, 'MaxCierre': {'$max': '$Cierre'}}},
                    # Agrupamos todos los ficheros que tengan elcierre maximo
                    {'$set': {'MaxVersion': {'$filter': {'input': '$UltimosDatos', 'cond': {'$eq': ['$$this.Cierre', '$$ROOT.MaxCierre']}}}}},
                    # De todos estos, sacamos la maxima version
                    {'$set': {'MaxVersion': {'$max': '$MaxVersion.Version'}}},
                    # Filtramos todos los documentos para tener el del maxima version y cierre (mas actual)
                    {'$set': {'UltimosDatos': {'$filter':{'input': '$UltimosDatos', 'cond': {'$and':[{'$eq':['$$this.Cierre', '$$ROOT.MaxCierre']}, 
                                                                                                        {'$eq':['$$this.Version', '$$ROOT.MaxVersion']}]}}}}},
                    {'$project':{'Datos': array_for_project}},{'$sort': {'_id.Periodo de datos':1}},
        
                    {'$set': {'UP_df': {'$filter': {'input': '$Datos', 'cond': {'$and':[{'$eq': ['$$this.UP', '$$ROOT._id.UP']},
                                                                                            {'$eq': ['$$this.Participante', '$$ROOT._id.Participante']}]}}}}},
                    {'$unwind': '$UP_df'},{'$replaceRoot':{'newRoot':'$UP_df'}},
                    {'$unwind': '$Datos'}, {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
                    {'$sort': {'Fecha':1, 'Temporada':-1}},
                    {'$set':{name:{'$replaceAll':{'input':f'${name}', 'find':',', 'replacement':'.'}} for name in ['Excedente']}},
                    {'$set':{'Fecha':{'$toDate':'$Fecha'}, 'Temporada':{'$toInt':'$Temporada'}, 'Excedente':{'$toDouble':'$Excedente'}}},
                    {'$set':{'Season':'$Temporada','UPR':'$UP','Energia':{'$divide':['$Excedente',1000]}}},
                    {'$project':{'_id':0, 'Periodo de datos':0, 'Datos':0, 'Temporada':0, 'UP':0, 'Excedente':0}}]
        result = pd.DataFrame([i for i in mongo_tera.CCH.SIMEL.aggregate(pipeline, allowDiskUse=True)])
        if not result.empty: 
            result.insert(result.columns.size, 'Segmento', 'Excedente')
            result = result.reindex(columns = sorted(result.columns.tolist(), key=REE.myfunc))
            if bool(headers): result  = result.filter(regex=f'(?i).*{headers}.*', axis=1)
        elif self.PrintWarning: raise ValueError(f'No hay archivos VERT en BBDD para {self.comer}, Date:{date}')
        return result
    
    @staticmethod
    def __verify_reganecu__(self, data:pd.DataFrame, 
                        headers:str=None, segmento:str=None)->pd.DataFrame:
        result = pd.DataFrame()
        mask_signo_energia = (data['Signo de la magnitud'] == 0) | (data['Signo de la magnitud'] == '0')
        data.loc[mask_signo_energia]['Signo de la magnitud'] = -1
        #---------- Aqui nos quedamos con los segmetos para tratar -------------
        if segmento !=None: data = data[data['Segmento'].str.contains(f'(?i){segmento}', regex=True)].reset_index(drop=True)

        groupper = ['UPR', 'Region','Cierre','Segmento']
        for group, df in data.groupby(groupper):
            
            if df.duplicated().any(): df = df[~df.duplicated()]
            if bool(headers): df  = df.filter(regex=f'(?i).*{headers}|signo de.*', axis=1)
            if group[-1] == 'DSV':
                df['Energia'], df['Importe'] = df['Energia']*df['Signo de la magnitud'], df['Importe']*df['Signo del importe']
                df = df.groupby(['Fecha', 'Season'], as_index=False).agg({'Energia':'sum', 'Precio':'mean', 'Importe':'sum'})
                data_complet = pd.DataFrame({key:[value]*len(df) for key, value in zip(groupper,group)})
                df = pd.concat([df, data_complet], axis=1)
            else:
                df['Importe'] = df['Importe']*df['Signo del importe'] #Agrupamos por fecha y temporada, ya que nos liquidan mas de una Hora
                if df[['Fecha', 'Season']].duplicated().any():
                    df = df.groupby(['Fecha', 'Season'], as_index=False).agg({'Energia':'sum', 'Importe':'sum'})
                    data_complet = pd.DataFrame({key:[value]*len(df) for key, value in zip(groupper,group)})
                    df = pd.concat([df, data_complet], axis=1)
                    df.insert(df.columns.size, 'Precio', (-1)*(df['Importe']/df['Energia']).round(4))
            result = pd.concat([result, df], axis=0)
            result = result.reindex(columns = sorted(result.columns.tolist(), key=REE.myfunc))
        return result

    @staticmethod
    def get_reganecu(self, date:str|datetime, 
                     hasta:Optional[str|datetime]=None,
                        *args, **kwargs)-> pd.DataFrame:
        print(datetime.now(), f'Buscando datos en REE, desde: {date}, hasta: {hasta}, empresa:{self.comer}')
        self = REE.__extractall_kwargs__(self, args, kwargs)
        result = pd.DataFrame()
        #------- Inputs ----------------
        if bool(kwargs): 
            headers = '|^'.join(next(iter(pd.Series(kwargs).filter(regex='(?i).*colum.*', axis=0).values)))
            segmento = '|^'.join(next(iter(pd.Series(kwargs).filter(regex='(?i).*segme.*', axis=0).values))) if 'segmento' in kwargs else None
        else: headers, segmento = None,None
        cierre = [self.kwargs.get('Tipo_cierre')] if 'Tipo_cierre' in self.kwargs.keys() else ['C2','C3', 'C4', 'C5']
        if isinstance(date, str): date = fecha_to_datetime(date)
        date = date.strftime('%Y-%m')
        region = [self.kwargs.get('Region')] if bool(self.kwargs) else pd.DataFrame(self.Infos)['region'].unique().tolist()
        #------------ Agrupamientos y Convert Formats ------------------
        group = {'Comercializadora': '$Comercializadora', 'Codecom':'$Codecom', 'Region': '$Region'}
        header_int = ['Season','Signo del importe','Signo de la magnitud','Facturacion'] 
        header_float = ['Energia MWh','Precio EUR/MWh','Importe EUR']

        pipeline = [{"$match": {"Comercializadora": {'$regex':self.comer, '$options':'i'},
                                'Region':{'$in':region}, 'Cierre':{'$in':cierre},
                                'Desde':{'$regex':date, '$options':'i'}}}]
        if cierre == None:
            pipeline += [{'$group':{'_id' :group,'UltimosDatos': {'$push':'$$ROOT'}, 'MaxCierre': {'$max': '$Cierre'}}},
                        {'$set': {'MaxCierreData': {'$filter': {'input': '$UltimosDatos', 'cond': {'$eq': ['$$this.Cierre', '$$ROOT.MaxCierre']}}}}},
                        {'$project':{'_id':0, 'MaxCierreData':1}},
                        {'$unwind':'$MaxCierreData'},
                        {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$MaxCierreData"]}}}]
            
        pipeline += [{'$project':{'_id':0,'Comercializadora':1, 'Codecom':1, 'Region':1,'Cierre':1, 'Datos':1}},
                    {'$unwind':'$Datos'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
                    {'$set':{name:{'$replaceAll':{'input':f'${name}', 'find':',', 'replacement':'.'}} for name in header_float}},
                    {'$set':{'Fecha':{'$toDate':'$Fecha'},
                              **{name:{'$toInt':f'${name}'} for name in header_int}, 
                                **{name:{'$toDouble':f'${name}'} for name in header_float}}},
                    {'$sort':{'Fecha':1}},
                    {'$set':{'UPR': '$Codigo de la UPR', **{name.split(' ')[0]: f'${name}' for name in header_float}}},
                    {"$project": {"_id": 0,'Datos':0, 'Codigo de la UPR':0, **{name:0 for name in header_float}}}]
        result_df = pd.DataFrame([i for i in self.mongo_tera['Compra_Energia']['Reganecu'].aggregate(pipeline, allowDiskUse=True)])
        if not result_df.empty: 
            result_df = result_df.reindex(columns = sorted(result_df.columns.tolist(), key=REE.myfunc))
            data = REE.__verify_reganecu__(self, result_df, headers, segmento)
            if not data.empty: 
                data = data.drop(columns=['Signo de la magnitud', 'Signo del importe'], errors='ignore')
                result = pd.concat([result, data], axis=0).reset_index(drop=True)          
        elif self.PrintWarning: raise ValueError(f'No hay liquidacion en la base de datos para {self.comer}, Date:{date}')
        return result
        
    def get_pantalla_reganecu(self, desde, 
                              *args, **kwargs) -> Callable[...,Any]:
        
        self = REE.__extractall_kwargs__(self, args, kwargs)
        if isinstance(desde, str): desde = fecha_to_datetime(desde)
        date = deepcopy(desde)
        bool_extruct_Data = self.kwargs.get('Matricial') == 'SI'

        if bool_extruct_Data: liquidacion = []
        else: liquidacion = pd.DataFrame()

        #----------Complet Hours of Month-------------
        hasta = desde.replace(day = calendar.monthrange(desde.year,desde.month)[-1])
        Date = pd.date_range(start=date.replace(day=1, hour=0), end=hasta.replace(hour=23), freq='H').to_frame(name='Fecha').reset_index(drop=True)
        Date = Añadir_cambios_horarios(Date['Fecha'])
        #----Extractall Headers in DataFrame ---------
        headers = ['Fecha', 'Season', 'UPR', 'Segmento']
        reganecu = REE.get_reganecu(self, date, columns = headers +['Precio', 'Energia$', 'Importe'])
        if not reganecu.empty:
            vert = self.get_vert(date, columns=headers +['Energia$'])
            if not vert.empty: reganecu = pd.concat([reganecu, vert], axis=0).fillna(0).reset_index(drop=True)
            #------  Relleno of Hours for Data ----------
            for group, df in reganecu.groupby(['UPR','Segmento']):
                upr, segmento = group[0], group[-1]
                name_upr = next(iter(df.filter(regex=r'(?i).*upr.*', axis=1).columns))
                missing_hour = Date[~Date.Fecha.isin(df.Fecha)]
                if not missing_hour.empty:
                    sort_columns = df.filter(regex=r'(?i).*date|fecha|hour.*', axis=1).columns.tolist()
                    df = pd.concat([df, missing_hour], axis=0)
                    df[['UPR', 'Segmento']] = upr, segmento
                    df = df.fillna(0).sort_values(by=sort_columns).reset_index(drop=True)
                    
                #---------Change Name Header of UPR---------  
                codecom = REE.__change_upr__(self, upr) if not upr.startswith('RB') else upr
                df[name_upr] = codecom
        
                if bool_extruct_Data:
                    #------------ Form Matricial for Data----------------
                    columns_rename = df.filter(regex=r'(?i).*ener|prec|impor.*', axis=1).columns.tolist()
                    df = df.drop(columns=['UPR', 'Segmento'], errors='ignore')
                    df = df.rename(columns={name:f'{name}_{codecom}_{segmento}' for name in columns_rename})
                    liquidacion.append(df)
                else: liquidacion = pd.concat([liquidacion,df], axis=0).fillna(0).reset_index(drop=True)

        if len(liquidacion)>0:
            if isinstance(liquidacion, list): liquidacion = functools.reduce(lambda l,r: pd.merge(l, r, how='outer', on=['Fecha', 'Season']), liquidacion)
            liquidacion.insert(1, 'Hora', liquidacion['Fecha'].dt.hour)
            liquidacion['Fecha'] = liquidacion['Fecha'].dt.strftime('%Y-%m-%d')
            if not bool_extruct_Data and self.kwargs.get('Total') == 'SI': 
                liquidacion = liquidacion.groupby(['UPR', 'Segmento'], as_index=False).agg({'Energia':'sum', 'Importe': 'sum'})
        elif isinstance(liquidacion, list): liquidacion = pd.DataFrame()   
        return liquidacion
    
    def get_infos_liquidacion(self, desde:str, 
                              *args, **kwargs) -> Callable[...,Any]:
        series = pd.DataFrame()
        REE.__extractall_kwargs__(self, args, kwargs)
        if isinstance(desde, str): desde = fecha_to_datetime(desde)
        date = deepcopy(desde)
        search = {'Comercializadora':{'$regex':f'(?i).*^{self.comer}.*', '$options':'i'}, 'Desde':{'$regex':date.strftime('%Y-%m')}}
        series = pd.DataFrame(self.mongo_tera['Compra_Energia']['Reganecu_1'].find(search, {'_id':0, 'Cierre':1, 'Region':1}))
        if not series.empty: series=series[~series.duplicated()].reset_index(drop=True)
        elif self.PrintWarning: raise ValueError(f'No se encontró informacion para la comer: {self.comer}, en la bbdd CodigosComerciales')
        return series
    
    
if __name__ == '__main__':

    infos = REE('PROFIT ENERGY', PrintWarning=False)
    results = infos.get_pantalla_reganecu(datetime(2023,7,1), kwargs ={'Tipo_cierre':'C2', 
                                                                       'Region':'peninsula', 
                                                                       'Matricial':'NO'})