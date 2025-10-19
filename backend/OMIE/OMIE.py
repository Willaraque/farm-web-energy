try:
    from Librerias.lib import *
    from Librerias.vars  import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)
    from Librerias.lib import *
    from Librerias.vars  import *

class OMIE:

    @staticmethod
    def myfunc(columns:str, dict_index:dict={}) -> str:
        '''Functions for reiindex of columns'''
        dict_index = {'Fecha':'0', 'Hora':'0', 'Season':'1', 'UPR':'2', 
                      'Segmento':'3', 'Energia':'4', 'Precio':'5', 'Importe':'6'}
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
                name = next(iter(value.keys()))
                self.kwargs = value.get(name)
            else: 
                self.args = value
        return self

    @staticmethod
    def __checkout_sistema__(self, sistema:str=None) -> dict:
        dic_result = {}
        if self.comer.startswith('IS'): search = {'comercializadora':{'$regex':f'(?i).*^{self.comer}.*', '$options':'i'}}
        else: search = {'codecom':{'$regex':f'(?i).*^{self.comer}.*', '$options':'i'}}
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
        if OMIE.__checkout_comer__(self, comer): self.comer = comer
        else: raise ValueError(f'La comercializadora, {comer} , no se encuentra en la base de datos[Codigos_Comerciales]')
        self.Infos = OMIE.__checkout_sistema__(self, sistema)
        if isinstance(self.Infos, dict) and len(self.Infos)>0:
            if 'comercializadora' in self.Infos.keys(): self.comer = self.Infos.get('comercializadora') 
        self.PrintWarning = PrintWarning
        self.group = group
        self.args = args
        self.kwargs = kwargs
        self = OMIE.__extractall_kwargs__(self, args, kwargs)

    @staticmethod
    def lookup_energy_TNP(self, data:pd.Series, 
                             desde:datetime|str,
                             one_day:bool=False, 
                             all_participacion:bool=False) -> pd.DataFrame:
        result = pd.DataFrame()
        #----- Validación variables entradas -------
        comer = self.comer.replace(' ', '_')
        desde = desde.strftime('%Y-%m')
        uof = [data[next(iter(data.filter(regex='(?i).*uof',axis=0).index))]]
        alias = data[next(iter(data.filter(regex='(?i).*alias',axis=0).index))]
        pipeline = [{"$match": {'Desde': {'$regex': desde},
                                'UPR':{'$in':uof}}},
                    {"$unwind": '$Compras'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Compras"]}}},
                    {'$set':{'Fecha':{'$toDate':'$Hora'}, 'Season':{'$toInt':'$Season'}, 'Energia':{'$toDouble':'$Energia'}}},
                    {'$project':{'_id':0,'Compras':0, 'Desde':0, 'Hasta':0,'UPR':0, 'Hora':0}}]
        result = pd.DataFrame(mongo_tera['Compra_Energia_Canaria'][alias].aggregate(pipeline, allowDiskUse=True))
        if not result.empty:
            result.insert(result.columns.size, 'UOF', uof[0])
            result = result.reindex(columns = sorted(result.columns.tolist(), key=OMIE.myfunc))
            result['Energia'] = result['Energia']*(-1)
            result.insert(result.columns.size, 'Tipo', 'Compra')
        elif self.PrintWarning: raise ValueError(f'No hay informacion en la bbdd *Compra_Energia_Canaria* para la comer: {comer}')
        return result


    @staticmethod
    def lookup_energy_OMIE(self, data:pd.Series, 
                             desde:datetime|str,
                            tipo:str='Compra', one_day:bool=False, 
                             all_participacion:bool=False) -> pd.DataFrame:
        
        result = pd.DataFrame()
        #----- Validación variables entradas -------
        comer = self.comer.replace(' ', '_')
        mask_comer = comer[:3] == 'ISM'
        Date = deepcopy(desde)
        desde = desde.strftime('%Y-%m')
        uof = [data[next(iter(data.filter(regex='(?i).*uof',axis=0).index))]]

        pipeline = [{"$match": {'Desde': {'$regex': desde},
                                'Comercializadora':{'$regex':f'{comer}'} ,'UOF':{'$in':uof}}}]
        if mask_comer: pipeline += [{"$match":{'Mercado':{'$ne':'continuo'}}}]
        pipeline += [{"$unwind": '$Datos'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Datos"]}}},
                    {'$project':{'_id':0, 'Desde':0, 'Hasta':0, 'Datos':0}},
                    {'$set':{'Fecha':{'$substr': [ "$Hora", 0, 10]}}},
                    {'$project':{'Comercializadora':1, 'UOF':1, 'Mercado':1,'Seccion':1, 
                                    'Hora':1, 'Season':1,'Energia':1,'Fecha':{'$concat':['$Fecha', 'T00:00:00']}}},
                    {'$group':{'_id':{'Fecha':'$Fecha'},
                                'Otros_Mercados':{'$push':{'Comercializadora':'$Comercializadora', 'UOF':'$UOF',
                                                            'Mercado':'$Mercado', 'Seccion':'$Seccion','Hora':'$Hora', 'Season':'$Season', 'Energia':'$Energia' }}}},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$_id"]}}},
                    {'$sort':{'Fecha':1}},
                    {'$lookup':{'from': "Operaciones_MC",
                                'let': {'date_coincidencia': "$Fecha"},
                                'pipeline' : [
                                            {'$match':{'$expr':{'$eq':['$$date_coincidencia', '$Fecha']}}},
                                            {'$unwind': '$Datos'},
                                            {'$match':{'Datos.IdUnidad':{'$in':uof}}},
                                            {'$set':{'Comercializadora':'ISM','UOF':'$Datos.IdUnidad','Mercado':'continuo', 
                                                    'Seccion':'$Seccion', 'Hora': "$Datos.Hora", #'Hora':{'$substr':[ "$Datos.FechaTransaccion", 0, 13]}
                                                     'Continuo':'$Datos.Energia', 'Precio':'$Datos.Precio'}}, #'Season_Cont':'1'
                                            {'$set':{'Continuo':{'$toDouble':'$Continuo'}, 'Precio':{'$toDouble':'$Precio'}}},
                                            {'$project': {'_id': 0, 'Comercializadora':1, 'UOF':1, 'Mercado':1, 'Seccion':1, 
                                                        'Hora':1,'Continuo':1, 'Precio':1}}], #'Hora':{'$concat':['$Hora',':00:00']} #'Season_Cont':1
                                'as': "Mercado_Continuo"}},
                    {"$project": {'Parametro':{"$concatArrays":[f'$Otros_Mercados','$Mercado_Continuo']}}},
                    {'$sort':{'_id.Fecha':1}},      
                    {'$unwind':'$Parametro'},
                    {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT","$Parametro"]}}}]    
        
        if one_day:  pipeline += [{'$match':{'$and':[{'Hora':{'$gte':desde[:10]+'T00:00:00'}},{'Hora':{'$lte':desde[:10]+'T23:00:00'}}]}}]
        pipeline  += [{'$set':{'Continuo':{'$cond': {'if':{ '$ifNull': ["$Continuo", False]}, 'then': '$Continuo', 'else': '0'}}}},
                            #    'Season_Continuo':{'$cond': {'if':{ '$ifNull': ["$Season_Cont", False]}, 'then': '$Season_Cont', 'else': '0'}}}},    
                        {'$set':{'Continuo':{'$toDouble':'$Continuo'}}}, #'Season_Continuo':{'$toDouble':'$Season_Continuo'}
                        {'$set':{'Energia': {'$sum': [ "$Energia", "$Continuo"]}}}, #'Season': {'$sum': [ "$Season", "$Season_Continuo"]}
                        # {'$set':{'Season':{ '$replaceAll':{'input': "$Season", 'find': " ", 'replacement': "1"}}}},
                        {'$set':{'Fecha':{'$toDate':'$Hora'}, 'Season':{'$toInt':'$Season'}}}, #'Energia':{'$toDouble':'$Energia'}
                        {'$project':{'_id':0,'Parametro':0, 'Comercializadora':0, 'Hora':0, 'Continuo':0}}] #'Season_Continuo':0, 'Season_Cont':0}}]                 
        result = pd.DataFrame(mongo_tera[f'{tipo}_Energia'][tipo].aggregate(pipeline, allowDiskUse=True))
        
        if not result.empty:
            if Date.month not in [3,10]:
                season = result['Season'].unique().tolist()[0]
                result.loc[result['Mercado']=='continuo','Season'] = season
            result = result.reindex(columns = sorted(result.columns.tolist(), key=OMIE.myfunc))
            if 'Compra' == tipo: result['Energia'] = result['Energia']*(-1)
            result.insert(result.columns.size, 'Tipo', tipo)
        elif self.PrintWarning: raise ValueError(f'No hay informacion en la bbdd {tipo} para la comer: {comer}')
        return result
    
    @staticmethod
    def __PreciosOMIE__(self, data:pd.DataFrame, 
                        desde:str|datetime) -> pd.DataFrame:
        result = pd.DataFrame()
        date = fecha_to_datetime(desde).strftime('%Y-%m') if isinstance(desde, str) else desde.strftime('%Y-%m')
        for group, df in data.groupby(['Tipo','Mercado', 'Seccion', 'UOF']):
            df = df.sort_values(by=['Fecha']).reset_index(drop=True)
            mercado, seccion = group[1].capitalize(), group[2]
            if not bool(re.findall(r'(?i).*continuo.*$', str(group))):
                pipeline = [{'$match':{'Fecha':{'$regex':f'{date}'},
                                       'Country':{'$regex':f'(?i)españ'}}},
                            {'$unwind':f'$Mercado_{mercado}'},
                            {"$replaceRoot": {"newRoot": {'$mergeObjects':["$$ROOT",f'$Mercado_{mercado}']}}},
                            {'$set':{'Hora':{'$toDate':'$Hora'}, 'Seccion':'MD'}} if mercado == 'Diario' else {'$set':{'Hora':{'$toDate':'$Hora'}, 'Seccion':'$Mercado'}},
                            {'$project':{'_id':0, 'Hora':1, 'Precio':1, 'Seccion':1}}]
                precio = pd.DataFrame(mongo_tera.Datos_De_Mercado.Precio_Energia_OMIE.aggregate(pipeline, allowDiskUse=True))
                if not precio.empty: 
                    if mercado != 'Diario':
                        mask_seccion = precio['Seccion'].str.contains(f'(?i).*{seccion}.*', regex=True)
                        precio = precio[mask_seccion].reset_index(drop=True)
                    df['Precio'] = precio['Precio']
            else: df['Seccion'] = f'Seccion'+df['Seccion']   
            result = pd.concat([result, df], axis=0).reset_index(drop=True)   
        if not result.empty:
            result['Importe'] = (result['Energia']*result['Precio']).round(2)
            result = result.reindex(columns = sorted(result.columns.tolist(), key=OMIE.myfunc))
        return result

    @staticmethod
    def __extractall_infos__(self, data:pd.Series|pd.DataFrame, 
                             desde:str|datetime, hasta:str|datetime,
                             one_day:bool=False,
                             all_partic:bool=False)->pd.DataFrame:
        result = pd.DataFrame()
        region = data[next(iter(data.filter(regex='(?i).*regi.*', axis=0).index))]
        if region.startswith('penin'):
            for tipo in ['Compra', 'Venta']:
                energia = OMIE.lookup_energy_OMIE(self, data, desde, tipo)
                if not energia.empty:
                    energia = OMIE.__PreciosOMIE__(self, energia, desde)
                    energia.insert(energia.columns.size, 'Region', region)
                    result = pd.concat([result, energia], axis=0)
        else: 
            energia = OMIE.lookup_energy_TNP(self, data, desde)
            if not energia.empty:
                precio, error = get_parametro_liquidacion(desde, hasta.replace(hour=23), f'SphvenDD_{region}')
                precio = precio.rename(columns={'datetime':'Fecha', 'Price':'Precio'}).drop(columns=['liquidation'], errors='ignore')
                energia = pd.concat([energia, precio['Precio']], axis=1)
                energia['Importe'] = (energia['Energia']*energia['Precio']).round(2)
                energia.insert(energia.columns.size, 'Region', region)
                result = pd.concat([result, energia], axis=0)

        if not result.empty: 
            result = result.groupby(['Fecha', 'Season', 'UOF', 'Region'], as_index=False).agg({'Energia':'sum', 'Importe':'sum'})
            result.insert(result.columns.size-1, 'Precio', [round(eur/ener,2) if ener !=0 else 0 for eur, ener in zip(result['Importe'],result['Energia'])])
        return result


    def get_energy(self, desde:str|datetime, 
                   hasta:str|datetime, region:str=[], 
                   *args, **kwargs) ->Callable[...,Any]:
        
        energia = pd.DataFrame()
        #-----------------   Inputs ------------------------------
        if isinstance(desde, str): desde = fecha_to_datetime(desde)
        if isinstance(hasta, str): hasta = fecha_to_datetime(hasta)
        print(datetime.now(), f'Buscando datos en OMIE, desde: {desde}, hasta: {hasta}, empresa:{self.comer}')
        if bool(self.Infos):
            infos = pd.DataFrame(self.Infos)
            energia = pd.concat(list(infos.apply(lambda data: OMIE.__extractall_infos__(self, data, desde, hasta), axis=1)))
            if not energia.empty: energia = energia.reset_index(drop=True)
                # columns = next(iter(energia.filter(regex='(?i).*ener.*',axis=1).columns))
                # energia[columns]= (energia[columns]*1000).abs()
                # energia = energia.rename(columns={columns:'PROGRAMADA (kWh)'})
            elif self.PrintWarning: raise ValueError(f'No se ha extraido informacion del proceso de ordenes de OMIE para la comer: {self.comer}')
        return energia

if  __name__ == '__main__':

    infos = OMIE('PROFIT ENERGY', PrintWarning=False).get_energy(datetime(2023,7,1), datetime(2023,7,31))
    