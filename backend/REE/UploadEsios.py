try:
    from Librerias.lib import *
    from Librerias.vars import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)
    from Librerias.lib import *
    from Librerias.vars  import *

from Utilities.extractall import Extractall

@dataclass
class InputsDatos:
    '''Inputs OBligatorios:
        - Begin: date with format correct -> str|datetime
        - end: date with format correct -> str|datetime'''
    start:str|datetime = "don't date format"
    end: str|datetime = "don't date format"

class UploadESIOS(InputsDatos):

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
                name = next(iter(value.keys()))
                self.kwargs = value.get(name)
            else: 
                self.args = value
        return self

    @staticmethod
    def __dropFilesEmpty__(self, path:str):
        import os
        dirname = str(deepcopy(path)).replace('\\', '/') 
        directory:list = os.listdir(dirname)
        for month in directory:
            sub_dirname = f'{dirname}/{month}'
            if os.path.exists(sub_dirname) and os.path.isdir(sub_dirname):
                if not os.listdir(sub_dirname):
                    if self.print: print(f"Borrando directorio vacio {sub_dirname}.")
                    os.rmdir(sub_dirname)
            elif self.warning: print(f"El directorio {sub_dirname} no existe.")

    def path_treat(self, 
                   path:str) -> pd.Series:
        results = pd.Series()
        if bool(os.listdir(path)):
            files = pd.to_datetime(pd.Series(os.listdir(path)), format='%Y%m')
            mask_month = (files >= self.start) & (files <= self.end)
            files = files[mask_month]
            if not files.empty:
                regex = deepcopy('|'.join(files.dt.strftime('%Y%m').tolist()))
                _df = pd.Series(glob.glob(f'{os.getcwd()}/Descargas/**/*.rar', recursive=True))
                _df_ = pd.Series(glob.glob(f'{os.getcwd()}/Descargas/**/*.zip', recursive=True))
                _df_ = pd.concat([_df, _df_], axis=0, join='outer').reset_index(drop=True)
                _df_ = _df_[_df_.str.contains(regex, regex=True)]
                if not _df_.empty: results = pd.concat([results, _df_], axis=0).reset_index(drop=True)
            elif self.warning: raise ValueError(f'No hay archivos para extraer, start: {self.start} y end: {self.end}')
        elif self.warning: print(f"El directorio {path} está vacio.")
        return results
    
    @staticmethod
    def __checkout__(self, columns) ->bool:
        return ('Date' or 'Hour') in columns.tolist()
    
    @staticmethod
    def __missingHours__(self, 
                         date:datetime,
                         df:pd.DataFrame)->pd.DataFrame:
        listrange = pd.DataFrame([i for i in range(1,25)], columns=['Hour'])
        listrange.insert(0,'Date', date)
        listrange.insert(listrange.columns.size,'Price', 0)
        missing = listrange[~listrange['Hour'].isin(df['Hour'])]
        if not missing.empty: df = pd.concat([df, missing], axis=0).sort_values(by='Hour').reset_index(drop=True)
        return df
    
    @staticmethod
    def __formatData__(self, 
                       data:pd.DataFrame)->pd.DataFrame:
        if not data.empty:
            data['Date'] = data['Date'].dt.strftime('%Y-%m-%dT%H:00:00')
            data['Precio'] = data['Precio'].apply(lambda x: str(x).replace('.', ','))
        return data
    
    def __fillHours__(self, 
                      data:pd.DataFrame)->None:
        results = pd.DataFrame()
        if UploadESIOS.__checkout__(self, columns=data.columns): 
            for group, df in data.groupby(['Date']):
                date_min, date_max = df['Date'].min().to_pydatetime(), df['Date'].max().to_pydatetime().replace(hour=23)
                df = UploadESIOS.__missingHours__(self, date=date_min, df=df)
                aux = FormatDate.Añadir_cambios_horarios(start=date_min, end=date_max, freq='H')
                df = pd.concat([aux, df.filter(regex='(?i)pre',axis=1).reset_index(drop=True)], axis=1)
                results = pd.concat([results, df], axis=0).reset_index(drop=True)
        elif self.warning: raise ValueError(f'No están las cabeceras ["date", "hour"] in data')
        return results
    
    def __uploadMongoDB__(self,
                    info:pd.DataFrame,
                    data:pd.DataFrame):
         for group, df in data.groupby([data['Date'].dt.day]):
            if 'Cierre' not in info.columns: info.insert(info.columns.size, 'Cierre', info['Tipo'].str.split('_').explode().reset_index(drop=True)[0])
            date = df.Date.min()
            filters = {'Fichero':'ESIOS - Mercado de electricidad',
                       'Emision': f"Fecha Emisión :{date.strftime('%d/%m/%Y')} - 00:00",
                       'Fecha':date.strftime('%Y-%m-%d')}
            info = info.drop(columns=['Month'], errors='ignore')
            filters.update(info.to_dict(orient='index')[0])

            df = UploadESIOS.__formatData__(self, data=df)

            if not mongo['Proyecto_Baterias']['ESIOS'].count_documents(filters):
                filters.update({'Datos':df.to_dict(orient='records')})
                mongo['Proyecto_Baterias']['ESIOS'].insert_one(filters)
                if self.print: print(f"{datetime.now()} Insert one document in Market: {filters.get('Tipo')}- Cierre: {filters.get('Cierre')}, Date: {date.strftime('%Y-%m-%d')}")
            else:
                dict_upload = deepcopy(filters)
                dict_upload.update({'Datos':df.to_dict(orient='records')})
                mongo['Proyecto_Baterias']['ESIOS'].replace_one(filters, dict_upload)
                if self.print: print(f"{datetime.now()} Replace one document in Market: {filters.get('Tipo')}- Cierre: {filters.get('Cierre')}, Date: {date.strftime('%Y-%m-%d')}")

    
    def __readFiles__(self, 
                      path:str,
                      search:list|str=['all']):
        paths = deepcopy(path).replace('\\', '/')
        search ='|'.join(search)
        regex = re.search(r'(?i)\d{1,6}.*', paths, re.IGNORECASE).group()
        list_info = regex.split('/')[0:2] + [regex.split('/')[-1]] if len(regex.split('/'))>3 else regex.split('/')
        info = pd.DataFrame([list_info], columns=['Month', 'Tipo', 'Nombre'])
        if not info.empty:
            data = pd.read_csv(paths, header=len(pd.read_csv(paths).columns), sep=';', na_filter=True).dropna(thresh=3, axis=1).dropna(thresh=3, axis=0)
            #Condicion para trabajar el Cuarto Horario, Me quedo con el ultimo cuarto horario
            data = QuarterHour(start=self.start, end=self.end, 
                                print=self.print, warning=self.warning, data=data).__get_Treat__(info=info, quarter=4) 
            data = UploadESIOS.__fillHours__(self, data=data)
            if not data.empty: self.__uploadMongoDB__(data=data, info=info)
        elif self.warning: raise ValueError(f'No hay cabeceras principales para anexar al docuemnto para subir a la bbdd')       
    
    def __extractall__(self, 
                       path:str, 
                       search:list):
        
        try: type = path.split('.')[-1]
        except: type = ''
        results = Extractall(path=path, 
                             warning=self.warning, 
                             print=self.print).get_extratac(type=type, search=search)
        if not results.empty: results.apply(lambda ruta: self.__readFiles__(path=ruta, search=search))
        elif self.warning: raise ValueError(f'No hemos podido extraer los documentos del .zip|.rar del path: {path}')


    def get_upload(self,
                   search:list=[''],
                   dropFiles:bool=True):
        path = f'{os.getcwd()}/Descargas/'
        if dropFiles: UploadESIOS.__dropFilesEmpty__(self, path=path)
        path_files = self.path_treat(path=path)
        if not path_files.empty: path_files.apply(lambda ruta: self.__extractall__(path=ruta, search=search))
        elif self.warning: raise ValueError(f'No tenemos las rutas para tratar los .zip|.rar')
        
    def __init__(self, start, end, 
                 path:str=...,
                 print:bool=False, warning:bool=False, 
                 date:Optional[str|datetime]=None,
                 *args, **kwargs) -> None:
        super().__init__(start, end)
        dates = FormatDate(start=start, end=end)
        if bool(dates): self.start, self.end = dates.start, dates.end
        self.print = print
        self.warning = warning
        self.args = args
        self.kwargs = kwargs
        self = UploadESIOS.__extractall_kwargs__(self, args, kwargs)


class LowDataError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        pass

    def __str__(self) -> str:
        super().__str__()
        return "Data should be not empty"

class QuarterHour(UploadESIOS):
    def __init__(self, start, end,
                 data:pd.Series|pd.DataFrame,
                 print:bool=False, warning:bool=False) -> None:
        super().__init__(start, end, data)
        if data.empty: 
            raise LowDataError
        else: self.data = data
        self.print = print
        self.warning = warning

    @staticmethod
    def __Quarter__(self, df, 
                    quarter) -> pd.DataFrame:
        rename_columns = ['Date', 'Hour', 'Quarter', 'Precio']
        if len(rename_columns) == len(df.columns):
            df.columns = rename_columns
            if 'Quarter' in df.columns: df = df[df['Quarter']==quarter].reset_index(drop=True)
            df.Hour = (df.Hour).astype(int)
            df.Date = pd.to_datetime(df.Date, format='%d/%m/%Y')
            df = df.drop(columns=['Quarter'], errors='ignore')
        elif self.warning: raise ValueError(f'El numero de header del data {len(df.columns)} != {len(rename_columns)}')
        return df
    
    def __DataTransforming__(self,
                             info:pd.DataFrame, 
                             data)->pd.DataFrame:
        result = pd.DataFrame()
        if not data.empty:
            data = data.reset_index()
            for group, df in data.groupby(['level_0']):
                dia = int(re.search(r'\d+',group).group())
                Date = datetime.strptime(info.Month.squeeze(), '%Y%m').replace(day=dia)
                range = pd.date_range(start=Date, end=Date.replace(hour=23), freq='H').to_frame(name='Date').reset_index(drop=True)
                df = df[df.columns[1:]].T.reset_index(drop=True)
                df.columns = ['Precio']
                df = pd.concat([range, df], axis=1).reset_index(drop=True)
                df.insert(1, 'Hour', df.index +1)
                df.Date = df.Date.apply(lambda date: date.replace(hour=0))
                result = pd.concat([result, df], axis=0).sort_values(by=['Date', 'Hour']).reset_index(drop=True)
        return result

    def __get_Treat__(self, 
                      info:pd.DataFrame=None, 
                      format:str='qh', 
                      quarter:int=4)->pd.DataFrame|pd.Series:
        
        df = self.data
        if 'qh' in info['Nombre'].squeeze().split('_')[1]:df = QuarterHour.__Quarter__(self, df=df, quarter=quarter)
        else:  df = self.__DataTransforming__(info=info, data=df)
        return df 



# class UploadLiquida:

#     @staticmethod
#     def myfunc(columns:str, dict_index:dict={}) -> str:
#         '''Functions for reiindex of columns'''
#         dict_index = {'Fecha':'0', 'Hora':'0', 'Season':'1', 'UPR':'2', 
#                       'Segmento':'3', 'Energia':'4', 'Precio':'5'}
#         for key, val in dict_index.items():
#             if columns in [key]: return val+columns
#         else: return columns

#     @staticmethod
#     def __decorator_kwargs__(fuction):
#         @functools.wraps(fuction) #wraps es un decorador de decoradores para traer los comentarios
#         def wrappers(*args, **kwargs):
#             self_input = list(args[1:])
#             for value in self_input:
#                 if isinstance(value, dict) or isinstance(value, tuple) and bool(value): #isinstance(value, dict|tuple)
#                     return fuction(*args, **kwargs)
#         return wrappers

#     @__decorator_kwargs__
#     def __extractall_kwargs__(self, *args, **kwargs):
#         '''Estamos extrayendo los kwargs y args de la clase OMIE'''
#         for value in list(args): 
#             if isinstance(value, dict) and bool(value): 
#                 name = next(iter(value.keys()))
#                 self.kwargs = value.get(name)
#             else: 
#                 self.args = value
#         return self

#     @staticmethod
#     def __checkout_sistema__(self, sistema:str=None) -> dict:
#         dic_result = {}
#         search = {'comercializadora':{'$regex':f'(?i).*^{self.comer}.*', '$options':'i'}}
#         projection = {'_id':0} if sistema == None else {'_id':0, 'upr':1}
#         dicts = pd.DataFrame(self.mongo_tera['Compra_Energia']['Codigos_Comerciales'].find(search, projection))
#         if not dicts.empty:
#             dic_result = deepcopy(dicts.to_dict(orient='records'))
#         elif self.PrintWarning: raise ValueError(f'No se encontró region para la comer: {self.comer}, en la bbdd CodigosComerciales')
#         return dic_result

#     @staticmethod
#     def __checkout_comer__(self, comer:str) -> bool:
#         series = pd.Series(self.mongo['Compra_Energia']['Codigos_Comerciales'].distinct('codecom'))
#         return series.str.contains(f'(?i).*{comer.upper()}.*').any()
    
#     @staticmethod
#     def __change_upr__(self, upr:str)->str:
#         search = {'upr':{'$regex':f'(?i).*^{upr}.*', '$options':'i'}}
#         series = pd.Series(self.mongo['Compra_Energia']['Codigos_Comerciales'].find_one(search, {'_id':0}))
#         if not series.empty: series = next(iter(series.filter(regex=r'(?i).*codecom.*',axis=0)))
#         elif self.PrintWarning: raise ValueError(f'No se encontró la UPR: {upr}, en la bbdd CodigosComerciales')
#         return series

#     def __init__(self, comer:str, PrintWarning:bool = True, #str|list
#                  sistema:str=None, group:str='all',
#                 *args, **kwargs) -> None:
        
#         self.mongo_tera = mongo
#         self.mongo_local = mongo
#         if UploadLiquida.__checkout_comer__(self, comer): self.comer = comer
#         else: raise ValueError(f'La comercializadora, {comer} , no se encuentra en la base de datos[Codigos_Comerciales]')
#         self.Infos = UploadLiquida.__checkout_sistema__(self, sistema)
#         if isinstance(self.Infos, dict) and len(self.Infos)>0:
#             if 'comercializadora' in self.Infos.keys(): self.comer = self.Infos.get('comercializadora') 
#         self.PrintWarning = PrintWarning
#         self.group = group
#         self.args = args
#         self.kwargs = kwargs
#         self = UploadLiquida.__extractall_kwargs__(self, args, kwargs)


#     @staticmethod
#     def get_vert(self, date, fichero:str='VERT', 
#                  TNP:bool=False, *args, **kwargs) -> pd.DataFrame: #str|datetime
        
#         result = pd.DataFrame()
#         #------ Inputs for search in BBDD CCH -> SIMEL --------
#         if bool(kwargs): headers = '|^'.join(next(iter(pd.Series(kwargs).filter(regex='(?i).*colum.*', axis=0).values)))
#         if isinstance(headers, list) and bool(headers): headers = '|'.join(headers)
#         if isinstance(date, str): date = fecha_to_datetime(date)
#         date = date.strftime('%Y-%m')
#         if bool(self.Infos):
#             Infos, region = pd.DataFrame(self.Infos), self.kwargs.get('Region')
#             Infos = Infos[Infos['provincia'].str.contains(f'(?i).*{region}.*', regex=True)]
#             if not Infos.empty: 
#                 expr_upr,code_ree = Infos['upr'].tolist(), Infos['coderee'].tolist()
#                 region = [i.capitalize() for i in Infos['region'].tolist()]

#         #-------- Agrupamiento -----------
#         group = {'Periodo de datos': '$Periodo de datos', 'UP': '$UP', 'Participante':'$Participante'}
#         numero_de_unwind, array_for_project, list_cierres = 2, '$UltimosDatos', ['H2','H3','HP', 'HC']
#         cases = [{'case':{'$eq':['$Periodo de cierre', tipo]}, 'then':index+1} for tipo, index in zip(list_cierres, range(len(list_cierres)))]
  
#         pipeline = [{'$match':{'Fichero':{'$regex':fichero, '$options':'i'},
#                                        'Region':{'$in':region},
#                                         'Periodo de datos':{'$regex':date, '$options':'i'},
#                                         'Participante':{'$in':code_ree},'UP':{'$in':expr_upr}}},
        
#                     {'$set': {'Cierre': {'$switch': {'branches': cases, 'default':0}},
#                       'Version': {'$toInt': '$Version'}}},
#                     # Agrupamos por dia y filtramos los documentos para tener el ultimo fichero del ultiom cierre y ultima version 
#                     {'$group':{'_id': group, 'UltimosDatos': {'$push':'$$ROOT'}, 'MaxCierre': {'$max': '$Cierre'}}},
#                     # Agrupamos todos los ficheros que tengan elcierre maximo
#                     {'$set': {'MaxVersion': {'$filter': {'input': '$UltimosDatos', 'cond': {'$eq': ['$$this.Cierre', '$$ROOT.MaxCierre']}}}}},
#                     # De todos estos, sacamos la maxima version
#                     {'$set': {'MaxVersion': {'$max': '$MaxVersion.Version'}}},
#                     # Filtramos todos los documentos para tener el del maxima version y cierre (mas actual)
#                     {'$set': {'UltimosDatos': {'$filter':{'input': '$UltimosDatos', 'cond': {'$and':[{'$eq':['$$this.Cierre', '$$ROOT.MaxCierre']}, 
#                                                                                                         {'$eq':['$$this.Version', '$$ROOT.MaxVersion']}]}}}}},
#                     {'$project':{'Datos': array_for_project}},{'$sort': {'_id.Periodo de datos':1}},
        
#                     {'$set': {'UP_df': {'$filter': {'input': '$Datos', 'cond': {'$and':[{'$eq': ['$$this.UP', '$$ROOT._id.UP']},
#                                                                                             {'$eq': ['$$this.Participante', '$$ROOT._id.Participante']}]}}}}},
#                     {'$unwind': '$UP_df'},{'$replaceRoot':{'newRoot':'$UP_df'}},
#                     {'$unwind': '$Datos'}, {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
#                     {'$sort': {'Fecha':1, 'Temporada':-1}},
#                     {'$set':{name:{'$replaceAll':{'input':f'${name}', 'find':',', 'replacement':'.'}} for name in ['Excedente']}},
#                     {'$set':{'Fecha':{'$toDate':'$Fecha'}, 'Temporada':{'$toInt':'$Temporada'}, 'Excedente':{'$toDouble':'$Excedente'}}},
#                     {'$set':{'Season':'$Temporada','UPR':'$UP','Energia':{'$divide':['$Excedente',1000]}}},
#                     {'$project':{'_id':0, 'Periodo de datos':0, 'Datos':0, 'Temporada':0, 'UP':0, 'Excedente':0}}]
#         result = pd.DataFrame([i for i in mongo_tera.CCH.SIMEL.aggregate(pipeline, allowDiskUse=True)])
#         if not result.empty: 
#             result.insert(result.columns.size, 'Segmento', 'Excedente')
#             result = result.reindex(columns = sorted(result.columns.tolist(), key=UploadLiquida.myfunc))
#             if bool(headers): result  = result.filter(regex=f'(?i).*{headers}.*', axis=1)
#         elif self.PrintWarning: raise ValueError(f'No hay archivos VERT en BBDD para {self.comer}, Date:{date}')
#         return result
    
#     def __verify_reganecu__(self, data:pd.DataFrame, 
#                         headers:str)->pd.DataFrame:
#         result = pd.DataFrame()
#         mask_signo_energia = (data['Signo de la magnitud'] == 0) | (data['Signo de la magnitud'] == '0')
#         data.loc[mask_signo_energia]['Signo de la magnitud'] = -1
#         if bool(headers): data  = data.filter(regex=f'(?i).*{headers}|signo de.*', axis=1)
#         for group, df in data.groupby(['UPR', 'Segmento']):
#             if df.duplicated().any(): df = df[~df.duplicated()]
#             if group[-1] == 'DSV':
#                 df['Energia'], df['Importe'] = df['Energia']*df['Signo de la magnitud'], df['Importe']*df['Signo del importe']
#                 df = df.groupby(['Fecha', 'Season'], as_index=False).agg({'Energia':'sum', 'Precio':'mean', 'Importe':'sum'})
#                 df.insert(2, 'UPR',group[0])
#                 df.insert(3, 'Segmento',group[-1])
#             else:
#                 df['Importe'] = df['Importe']*df['Signo del importe'] #Agrupamos por fecha y temporada, ya que nos liquidan mas de una Hora
#                 if df[['Fecha', 'Season']].duplicated().any():
#                     df = df.groupby(['Fecha', 'Season'], as_index=False).agg({'Energia':'sum', 'Importe':'sum'})
#                     df.insert(2, 'UPR',group[0])
#                     df.insert(3, 'Segmento',group[-1])
#                     df.insert(5, 'Precio', (-1)*(df['Importe']/df['Energia']).round(4))
#             result = pd.concat([result, df], axis=0)
#         return result

#     @staticmethod
#     def reganecu(self, date:str|datetime, hasta:str|datetime=None,
#                  *args, **kwargs,
#                  )-> pd.DataFrame:
        
#         result = pd.DataFrame()
#         #------- Inputs ----------------
#         if bool(kwargs): headers = '|^'.join(next(iter(pd.Series(kwargs).filter(regex='(?i).*colum.*', axis=0).values)))
#         cierre = self.kwargs.get('Tipo_cierre') if 'Tipo_cierre' in self.kwargs.keys() else None
#         if isinstance(date, str): date = fecha_to_datetime(date)
#         date = date.strftime('%Y-%m')
#         region = self.kwargs.get('Region')
#         #------------ Agrupamientos y Convert Formats ------------------
#         group = {'Comercializadora': '$Comercializadora', 'Codecom':'$Codecom', 'Region': '$Region'}
#         header_int = ['Season','Signo del importe','Signo de la magnitud','Facturacion'] 
#         header_float = ['Energia MWh','Precio EUR/MWh','Importe EUR']

#         pipeline = [{"$match": {"Comercializadora": {'$regex':self.comer, '$options':'i'},
#                                 'Region':{'$regex':f'(?i).*{region}.*'}, 'Cierre':cierre,
#                                 'Desde':{'$regex':date, '$options':'i'}}}]
#         if cierre == None:
#             pipeline += [{'$group':{'_id' :group,'UltimosDatos': {'$push':'$$ROOT'}, 'MaxCierre': {'$max': '$Cierre'}}},
#                         {'$set': {'MaxCierreData': {'$filter': {'input': '$UltimosDatos', 'cond': {'$eq': ['$$this.Cierre', '$$ROOT.MaxCierre']}}}}},
#                         {'$project':{'_id':0, 'MaxCierreData':1}},
#                         {'$unwind':'$MaxCierreData'},
#                         {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$MaxCierreData"]}}}]
            
#         pipeline += [{'$project':{'_id':0,'Comercializadora':1, 'Codecom':1, 'Cierre':1, 'Datos':1}},
#                     {'$unwind':'$Datos'},
#                     {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
#                     {'$set':{name:{'$replaceAll':{'input':f'${name}', 'find':',', 'replacement':'.'}} for name in header_float}},
#                     {'$set':{'Fecha':{'$toDate':'$Fecha'},
#                               **{name:{'$toInt':f'${name}'} for name in header_int}, 
#                                 **{name:{'$toDouble':f'${name}'} for name in header_float}}},
#                     {'$sort':{'Fecha':1}},
#                     {'$set':{'UPR': '$Codigo de la UPR', **{name.split(' ')[0]: f'${name}' for name in header_float}}},
#                     {"$project": {"_id": 0,'Datos':0, 'Codigo de la UPR':0, **{name:0 for name in header_float}}}]
#         result_df = pd.DataFrame([i for i in self.mongo_tera['Compra_Energia']['Reganecu'].aggregate(pipeline, allowDiskUse=True)])
#         if not result_df.empty: 
#             result_df = result_df.reindex(columns = sorted(result_df.columns.tolist(), key=UploadLiquida.myfunc))
#             data = self.__verify_reganecu__(result_df, headers)
#             if not data.empty: 
#                 data = data.drop(columns=['Signo de la magnitud', 'Signo del importe'], errors='ignore')
#                 result = pd.concat([result, data], axis=0).reset_index(drop=True)          
#         elif self.PrintWarning: raise ValueError(f'No hay liquidacion en la base de datos para {self.comer}, Date:{date}')
#         return result
        
#     def get_upload_ree(self, desde, 
#                               *args, **kwargs) -> Callable[...,Any]:
        
#         self = UploadLiquida.__extractall_kwargs__(self, args, kwargs)
#         if isinstance(desde, str): desde = fecha_to_datetime(desde)
#         date = deepcopy(desde)
#         bool_extruct_Data = self.kwargs.get('Matricial') == 'SI'

#         if bool_extruct_Data: liquidacion = []
#         else: liquidacion = pd.DataFrame()

#         #----------Complet Hours of Month-------------
#         hasta = desde.replace(day = calendar.monthrange(desde.year,desde.month)[-1])
#         Date = pd.date_range(start=date.replace(day=1, hour=0), end=hasta.replace(hour=23), freq='H').to_frame(name='Fecha').reset_index(drop=True)
#         Date = Añadir_cambios_horarios(Date['Fecha'])
#         #----Extractall Headers in DataFrame ---------
#         headers = ['Fecha', 'Season', 'UPR', 'Segmento']
#         reganecu = UploadLiquida.reganecu(self, date, columns = headers +['Precio', 'Energia$', 'Importe'])
#         if not reganecu.empty:
#             vert = UploadLiquida.get_vert(self, date, columns=headers +['Energia$'])
#             if not vert.empty: reganecu = pd.concat([reganecu, vert], axis=0).fillna(0).reset_index(drop=True)
#             #------  Relleno of Hours for Data ----------
#             for group, df in reganecu.groupby(['UPR','Segmento']):
#                 upr, segmento = group[0], group[-1]
#                 name_upr = next(iter(df.filter(regex=r'(?i).*upr.*', axis=1).columns))
#                 missing_hour = Date[~Date.Fecha.isin(df.Fecha)]
#                 if not missing_hour.empty:
#                     sort_columns = df.filter(regex=r'(?i).*date|fecha|hour.*', axis=1).columns.tolist()
#                     df = pd.concat([df, missing_hour], axis=0)
#                     df[['UPR', 'Segmento']] = upr, segmento
#                     df = df.fillna(0).sort_values(by=sort_columns).reset_index(drop=True)
                    
#                 #---------Change Name Header of UPR---------  
#                 codecom = UploadLiquida.__change_upr__(self, upr) if not upr.startswith('RB') else upr
#                 df[name_upr] = codecom
        
#                 if bool_extruct_Data:
#                     #------------ Form Matricial for Data----------------
#                     columns_rename = df.filter(regex=r'(?i).*ener|prec|impor.*', axis=1).columns.tolist()
#                     df = df.drop(columns=['UPR', 'Segmento'], errors='ignore')
#                     df = df.rename(columns={name:f'{name}_{codecom}_{segmento}' for name in columns_rename})
#                     liquidacion.append(df)
#                 else: liquidacion = pd.concat([liquidacion,df], axis=0).fillna(0).reset_index(drop=True)

#         if len(liquidacion)>0:
#             if isinstance(liquidacion, list): liquidacion = functools.reduce(lambda l,r: pd.merge(l, r, how='outer', on=['Fecha', 'Season']), liquidacion)
#             liquidacion.insert(1, 'Hora', liquidacion['Fecha'].dt.hour)
#             liquidacion['Fecha'] = liquidacion['Fecha'].dt.strftime('%Y-%m-%d')
#             if not bool_extruct_Data and self.kwargs.get('Total') == 'SI': liquidacion = liquidacion.groupby(['UPR', 'Segmento'], as_index=False).agg({'Energia':'sum', 'Importe': 'sum'})
#         elif isinstance(liquidacion, list): liquidacion = pd.DataFrame()   
#         return liquidacion
    
# ##AQUI WILL VA A IMPLEMENTAR LA NUEVA CLASE PARA SUBIR LAS LIQUIDACIONES
    
# def modificar_subgroups(infos:pd.DataFrame, region:str|list):
#     dia, upr, segmento = infos['Fecha'].unique().tolist()[0], infos['UPR'].unique().tolist()[0], infos['Segmento'].unique().tolist()[0]
#     # maks_drop_columns_signos = infos.filter(regex='(?i).*signo.*',axis=1).columns.tolist()
#     if upr.startswith('RB') and segmento == 'DSV' or segmento=='IEAD':
#         if upr.startswith('RB') and segmento == 'DSV':
#             pass
#         infos['Energia'] = infos['Energia']*infos['Signo_magnitud']
#         infos['Importe'] = infos['Importe']*infos['Signo_importe']  
#     else:
#         infos['Importe'] = infos['Importe']*infos['Signo_importe']

#     def duplicated_hours_segmento(series:pd.DataFrame):
#         list_precios = series['Precio'].unique().tolist()
#         mask_number_prices = len(list_precios) == 1
#         if mask_number_prices:
#             series = series.groupby(['Fecha', 'UPR', 'Segmento', 'Hora'], as_index=False).agg({'Precio':'mean', 'Energia':'sum', 'Importe':'sum'})
#         else:
#             series = series.groupby(['Fecha','Hora', 'UPR','Segmento'], as_index=False).agg({'Energia':'sum', 'Importe':'sum'})
#             series['Precio'] = (series['Importe'] / series['Energia'].astype(float)).round(4)
#         return series
    
#     infos = infos.groupby(['Fecha', 'UPR', 'Segmento', 'Hora'], as_index=False).apply(lambda x: duplicated_hours_segmento(x))
#     infos['Signo_importe'] = [1 if i>=0 else -1 for i in infos['Importe']]
#     infos['Signo_magnitud'] = [1 if i>=0 else -1 for i in infos['Energia']]
#     infos['Importe'] = [round(abs(i),2) for i in infos['Importe']]
#     infos['Energia'] = [round(abs(i),3) for i in infos['Energia']]

#     #---- Completamos horas del día --------
#     dates_complet = pd.date_range(start=dia, end=dia.replace(hour=23), freq='H').to_frame(name='Fecha').reset_index(drop=True)
#     change_hour = Añadir_cambios_horarios(dates_complet['Fecha'])[['Fecha', 'Season']]
#     infos['Fecha'] = infos[['Fecha', 'Hora']].apply(lambda x: x['Fecha'].replace(hour=x['Hora']) if x['Hora']!=24 else x['Fecha'].replace(hour=2), axis=1)
#     infos = infos.drop(['Hora'], axis=1).reset_index(drop=True)
#     mask_horas_not_coincididas = dates_complet['Fecha'].isin(infos['Fecha'])
#     horas_not_coincididas = dates_complet[~mask_horas_not_coincididas].reset_index(drop=True)

#     #----------- Añadimos lo del cambio horario ----------
#     copy_infos = pd.concat([infos, horas_not_coincididas], axis=0)
#     copy_infos = copy_infos.sort_values(by='Fecha').reset_index(drop=True).fillna(0)
#     copy_infos = copy_infos.drop(['Fecha'], axis=1)
#     copy_infos = pd.concat([change_hour, copy_infos], axis=1).reset_index(drop=True)
#     copy_infos['UPR'], copy_infos['Segmento'] = upr, segmento
#     infos = deepcopy(copy_infos)
#     columns_int = infos.filter(regex='(?i).*signo.*', axis=1).columns.tolist()
#     infos[columns_int] = infos[columns_int].fillna(0).astype(int)
#     return infos

# def __Change_Hours__(date:str|datetime) ->datetime:
#     if isinstance(date, str): date = fecha_to_datetime(date).to_pydatetime()
#     desde = deepcopy(date).replace(day=1)
#     hasta = desde.replace(day = calendar.monthrange(desde.year,desde.month)[-1])
#     Date = pd.date_range(start=desde.replace(hour=0), end=hasta.replace(hour=23), freq='H').to_frame(name='Date').reset_index(drop=True)
#     Date['weekday'] = Date['Date'].dt.day_of_week
#     last_sunday_month = Date['Date'][Date['weekday'] == 6].iloc[-1].to_pydatetime()
#     return last_sunday_month

# def __Añadir_Season__(data:pd.DataFrame, last_sunday_month:datetime):
#     result = pd.DataFrame()
#     for group, df in data.groupby(['Fecha', 'Season', 'Codigo de la UPR', 'Codigo del precio']):
#         #-----Extraccion de los Values principales a utilizar ---------
#         date = next(iter(df['Fecha'].unique())).to_pydatetime()
#         if isinstance(date, str): date = fecha_to_datetime(date).to_pydatetime()

#         #-------- Meses en los que hay cambio horarios -----------
#         if date.month == 3:
#             #------- Nos quitan la hora 2 en los archivos ---------
#             mask_hora = df['Hora'] >=2
#             df.loc[~mask_hora, 'Season'] = 0
#             df.loc[mask_hora, 'Hora'] = df.loc[mask_hora, 'Hora'] + 1
#             df['Fecha'] = [date.replace(hour=hora) for date, hora in zip(df['Fecha'], df['Hora'])]
#             result = pd.concat([result, df], axis=0).reset_index(drop=True)

#         elif date.month == 10:
#             #------- Cambiamos la hora 24 en los archivos, para pasarlo al formato datetime ---------
#             mask_hora = df['Hora'] <=2
#             df.loc[mask_hora, 'Season'] = 1
#             df.loc[~mask_hora, 'Season'] = 0
#             df.loc[df['Hora'] == 24, ['Hora', 'Season']] = 2, 0
#             df['Fecha'] = [date.replace(hour=hora) for date, hora in zip(df['Fecha'], df['Hora'])]
#             result = pd.concat([result, df], axis=0).reset_index(drop=True)    
#     return result


# def tratamiento_reganecu(Series:pd.Series, name_archivo:str, region:str):
#     ruta, dia = Series['Fichero'], Series['Fecha']
#     fecha = dia.strftime('%Y-%m-%d')
#     result = pd.DataFrame()
#     info = pd.read_csv(ruta, sep = ',')[f'{name_archivo};'].str.split(';', expand=True)
#     mask_empty_archivo = info.empty or  info.values[0][0] == '*'
#     if not mask_empty_archivo:
#         #-------- Asignamos cabeceras a los nombre de los archivos del reganecu -------------
#         info = info.drop(columns=[24,25], errors='ignore') #La columna 24,25, son adiccionales a lo del Reganecu
#         if len(info.columns) == len(headers_peninsula): info.columns = headers_peninsula
#         else: raise ValueError(f'Cambiarion la cantidad de cabeceras en el reganecu para {name_archivo}')

#         #--------- Mineria de datos ---------------
#         info = info.filter(regex='(?i).*^((?!^reservado nul).)*$', axis=1)
#         info = info.dropna(axis=0, thresh=10).reset_index(drop=True) #elimina las filas, que tengan mas de 10 None|Nan
#         columns_date = next(iter(info.filter(regex='(?i).*fecha', axis=1).columns))
#         info[columns_date] = info[columns_date].apply(lambda date: fecha_to_datetime(date))
#         info['Hora'] = info['Hora'].astype(int) - 1
#         info = info.sort_values(by=['Fecha', 'Hora', 'Codigo de la UPR']).reset_index(drop=True)

#         #--------- Añadimos Temporada y Cambio Horario -------------
#         date = next(iter(info['Fecha'].unique())).to_pydatetime()
#         summer = date.month >= 3 and date.month <= 10
#         if summer: info.insert(1,'Season',1)
#         else: info.insert(1,'Season',0)

#         if date.month in [3,10]: 
#             last_sunday_month = __Change_Hours__(date)
#             if date.month == 3: less_than, greater = 0,1
#             else:less_than, greater = 1,0

#             #Condiciones para aplicar el cambio horario 
#             if date.day < last_sunday_month.day: info['Season'] = less_than
#             elif date.day == last_sunday_month.day: info = __Añadir_Season__(info, last_sunday_month)
#             else: info['Season'] = greater

#         info['Fecha'] = [date.replace(hour=hora) for date, hora in zip(info['Fecha'], info['Hora'])]
#         info = info.drop(columns=['Hora'], errors='ignore')
#         info = info.applymap(lambda x: str(x).strip().replace('.',','))
#         info['Fecha'] = pd.to_datetime(info['Fecha'], format='%Y-%m-%d %H:00:00')
#         result = pd.concat([result, info], axis=0)
#     return result

# def upload_liquidacion(data:pd.DataFrame, comercial:str, fichero:str, region:str|list):

#     #------ Keys Principales, para guardar en la nueva base de datos -------
#     desde =  data['Fecha'].min().replace(day=1)
#     hasta = desde.replace(day = calendar.monthrange(desde.year,desde.month)[-1]).replace(hour=23)
#     upr = next(iter(data['Codigo de la UPR'].unique()))
#     segmento = next(iter(data['Segmento'].unique()))
#     cierre = fichero[:2]

#     #--------- Creamos el filters con los campos principales para subir a la base de datos *----------
#     filters = {'Fichero':fichero, 'Desde': desde.isoformat(), 'Hasta': hasta.isoformat(), 
#               'Comercializadora': comercial, 'Segmento':segmento,  'UPR':upr, 'Cierre': cierre}

#     search = {'upr':upr,'comercializadora':comercial} if not upr.startswith('RB') else {'$or':[{'upr':upr},{'comercializadora':comercial}]} #'activo':True
#     result = [i for i in db_tera.Compra_Energia.Codigos_Comerciales.find(search,{'_id':0})]    
#     if bool(result):
#         result = result[0]
#         filters.update({'Comercializadora':result['comercializadora'], 'Region': result['region'],
#                        'Provincia':result['provincia'], 'Codecom':result['codecom']})
#     else: raise ValueError(f'No hay informacion de la comercializadora para la COMER:{comercial} - UPR:{upr}')
#     data['Fecha'] = data['Fecha'].dt.strftime('%Y-%m-%dT%H:00:00')

#     #------ Upload de la liquidacion a la base de datos
#     if not db_tera.Compra_Energia.Reganecu.count_documents(filters):
#         filters.update({'Datos':data.to_dict('records')})
#         db_tera.Compra_Energia.Reganecu.insert_one(filters) # Will está llenando la base de datos nueva, para despues modifcar, lo que haga falta
#     else:
#         document_replace = deepcopy(filters)
#         document_replace.update({'Datos':data.to_dict('records')})
#         db_tera.Compra_Energia.Reganecu.replace_one(filters, document_replace)

# def update_liquidaciones(path_carpeta_upr:str, cierre:str, comercializadora:str, fichero:str):
    
#     read_file = pd.DataFrame(os.listdir(path_carpeta_upr), columns=['Fichero'])
#     dict_region = {'SEIErega': ['baleares','canarias'], 'reganecu':'peninsula'} #dict_region = {'SEIErega': ['baleares','canarias'], 'reganecu':'peninsula'}
#     for name_archivo, region in  dict_region.items(): #['reganecu', 'liquidia']
#         maks_name_ree = f'.*(?i){cierre}_{name_archivo}*'
#         ruta_reganecu = read_file[read_file['Fichero'].str.contains(maks_name_ree, regex=True)].reset_index(drop=True)
#         if not ruta_reganecu.empty:
#             ruta_reganecu = ruta_reganecu.drop_duplicates().sort_values(by='Fichero') if ruta_reganecu.duplicated().any() else ruta_reganecu.sort_values(by='Fichero') 
#             ruta_reganecu['Fecha'] = ruta_reganecu['Fichero'].str.split('_',expand=True).iloc[:, -2]
#             ruta_reganecu['Fecha'] = pd.to_datetime(ruta_reganecu['Fecha'], format='%Y%m%d')
#             ruta_reganecu['Fichero'] = path_carpeta_upr + ruta_reganecu['Fichero']
#             print(f'{datetime.now()} Inicio tratamiento archivos {name_archivo}')
#             reganecu = list(ruta_reganecu.apply(lambda values: tratamiento_reganecu(values, name_archivo, region), axis=1))
#             print(f'{datetime.now()} Finalizado tratamiento archivos {name_archivo}')
#             if bool(reganecu): 
#                 reganecu = pd.concat(reganecu, axis=0, join='outer').reset_index(drop=True)
#                 reganecu.groupby(['Codigo de la UPR', 'Segmento'], group_keys=False).apply(lambda data: upload_liquidacion(data, comercializadora, fichero, region))
#                 print(f'{datetime.now()} Se subio correctamente la liquidacion de {name_archivo}')
#         else:
#             print(f'{datetime.now()} No hay archivos de {name_archivo} para {comercializadora} : {cierre} - {region}')

# def archivos_tratar(Series:pd.Series):
#     comercial, cierre, date, date_str = Series['Comercial'], Series['Cierre'], Series['Fecha'], Series['Fecha'].strftime('%Y%m')
#     path_utilizar, comer_Search = path_usar(date, comercial)
#     #------- Creamos la carpeta de desacarga, por si no existe ---------
#     if os.path.exists(path_utilizar):
#         infos_liquidaciones = pd.Series(os.listdir(path_utilizar)).reindex(pd.Series(os.listdir(path_utilizar)))
#     else:
#         [os.makedirs(i) for i in [path_utilizar] if not os.path.exists(i)]
#         infos_liquidaciones = pd.Series(os.listdir(path_utilizar))
    
#     #------ Buscando los archivos de las liquidaciones
#     if len(infos_liquidaciones)>0:
#         mask_liquidacion = '(?i).*' + f'{cierre}_liquidacion_{comercial}_{date_str}[.]\d+[.]zip$|{cierre}_liquidacion_{comer_Search}_{date_str}[.]\d+[.]zip$'+ '.*' #[.]\d+[.]zip
#         infos_liquidaciones = infos_liquidaciones.filter(regex=mask_liquidacion, axis=0).fillna(1)
#         if len(infos_liquidaciones)>0:
#             if len(infos_liquidaciones)>1: infos_liquidaciones = infos_liquidaciones.sort_values().iloc[[-1]]
#             infos_liquidaciones = pd.Series(infos_liquidaciones.index.tolist(), index=['Liquidacion']) 
#             infos_liquidaciones['path_liquidacion'] = path_utilizar + infos_liquidaciones.values[0]
#         else:
#             infos_liquidaciones = pd.Series([0,0], index=['Liquidacion', 'path_liquidacion'])
#     else:
#         # print(f'No hay liquidacion descargada: {cierre}_liquidacion_{comer_Search}_{date_str}')
#         infos_liquidaciones = pd.Series([0,0], index=['Liquidacion', 'path_liquidacion'])
#     Series = pd.concat([Series, infos_liquidaciones], axis=0)
#     return Series

# def extratc_zip(path_work :str, mes:datetime, cierre: str, name_cierre:str, comercial:str='All'):
#     bool_extrac, password, zipfilename, month_str = True, None, path_work, mes.strftime('%Y%m')
#     path_carpeta_upr = path_reganecu + comercial + '/' + month_str + '/' + cierre + '/'
#     [os.makedirs(i) for i in [path_carpeta_upr] if not os.path.exists(i)]
#     # open and extract all files in the zip
#     if isinstance(zipfilename, str):
#         archivo_zip = zipfile.ZipFile(zipfilename, "r")
#         infos_zip = pd.Series(archivo_zip.namelist())
#         mask_zip = infos_zip.str.contains(f'{cierre}_reganecu|reganecu|{cierre}_SEIErega', regex=True)
#         infos_zip = infos_zip[mask_zip].reset_index(drop=True)
#         try:
#             print(f'Se han extraído {len(infos_zip)} ficheros de la liquidacion {name_cierre}')
#             infos_zip.apply(lambda reganecu: archivo_zip.extract(reganecu, path_carpeta_upr) if not reganecu in path_carpeta_upr else 0)
#             bool_extrac = True
#         except:
#             bool_extrac = False
#             pass
#         archivo_zip.close()
#     return bool_extrac, path_carpeta_upr

# def main_multiprocessing(index:int, comercial:str, cierre:str, mes:datetime, name_liqui:str, path_liqui:str):
#     bool_extrac, path_carpeta_upr = extratc_zip(path_liqui, mes, cierre, name_liqui, comercial)
#     if bool_extrac:
#         update_liquidaciones(path_carpeta_upr, cierre, comercial, name_liqui) #Subir los datos a Mongo
#         '''Mover los archivos de la carpeta de trabajo a otro directorio,para especificar que ya fueron tratados o eliminar con el os.remove()'''
#         if os.listdir(path_carpeta_upr) != []:
#             pd.Series(os.listdir(path_carpeta_upr)).apply(lambda row: os.remove(path_carpeta_upr + row) if row in os.listdir(path_carpeta_upr) else 0)
#         print(f'Ha finalizado el proceso {mes}: {cierre} - {comercial}'.center(70,'-'))



    
# if __name__ == '__main__':

#     infos = UploadLiquida('PROFIT ENERGY', PrintWarning=False)
#     results = infos.get_upload_ree(datetime(2023,7,1), datetime(2023,12,1), kwargs ={'Tipo_cierre':'C2', 
#                                                                        'Region':'peninsula', 
#                                                                        'Matricial':'NO'})
    
#     ''' Los cierres implican liquidacion economica a los sujetos mientras que las anotaciones no
#             -  Se toman los archivos 2.zip que comienzan a partir del A3 para las liquidaciones, ya que el A2 varia por fechas, y se van tomando las cierres mas actualizados
#                         que ban de manera acendente, esto es : A3 -> A4 -> A5 -> C1 -> ... -> C5 
#             - Para liquidar la energía sobre las que representamos, utilizamos el C2 que es la liquidación mas actualizada'''

#     Desde = datetime(2023,5,1)
#     # Hasta = Desde.replace(day = calendar.monthrange(Desde.year,Desde.month)[-1])
#     Hasta = datetime(2023,5,31)
#     date_range = pd.date_range(start = Desde, end = Hasta ,freq = 'MS').to_list()
#     comercial = ['PROFIT ENERGY'] #['ISM','HELIOS', 'AHORALUZ', 'PROFIT ENERGY', 'COMUNIDAD SOLAR', 'AED', 'CRECESOL'] Pasas el nombre de la comercializadora a la cual quieres, tratar lo reganecus
#     tipo_cierre = ['C2'] #['A3','A4','A5', *[f'C{i}' for i in range(1,6)]]

#     #------- Condiciones de busqueda de cierres, avances---------
#     combinaciones = pd.DataFrame([{'Comercial': comer, 'Cierre':cierr, 'Fecha':date} for comer in comercial for cierr in tipo_cierre for date in date_range])
#     combinaciones = combinaciones.apply(lambda x: archivos_tratar(x), axis=1)
#     mask_to_tratar = (combinaciones['Liquidacion'] ==0) | (combinaciones['path_liquidacion']==0)
#     liquidacion_a_tratar, errores = combinaciones[~mask_to_tratar].reset_index(drop=True),combinaciones[mask_to_tratar].reset_index(drop=True)

#     if len(liquidacion_a_tratar)>0:
#         try:
#             hw_cores = int(mp.cpu_count()/2) + 1
#             liquidaciones = list(liquidacion_a_tratar.itertuples(name=None))
#             if len(liquidaciones) > 0:
#                 print({f' --- INICIANDO LECTURA CON MULTIPROCESSING DE {len(liquidaciones)} con {hw_cores} Cores ---'.center(80,'-')})
#                 with Pool(hw_cores) as pool:
#                     pool.starmap(main_multiprocessing, liquidaciones)
#                 print({f'--- FIN DE LECTURA CON MULTIPROCESSING PARA: {comercial} ---'.center(80,'-')})
#         except Exception as err:
#             print(err)
#     else:
#         print({f" --- NO HAY LIQUIDACION PARA LEER EN {comercial} ---".center(80,'-')})