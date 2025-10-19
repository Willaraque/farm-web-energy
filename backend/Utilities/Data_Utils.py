from Librerias.lib import *
from Librerias.vars import *

class DataUtils:

    @staticmethod 
    def __combinations__(cls:Optional[type], 
                         range:pd.DataFrame,
                         df:dict={})->pd.DataFrame:
        
        result = pd.DataFrame([], columns=['Año','Mercado', 'Archivo', 'Website'])
        if hasattr(cls, 'markets'):
            if bool(cls.markets):
                result = pd.DataFrame(cls.markets)
                years = pd.DataFrame(range[range.columns[-1]].dt.year.unique().tolist(), columns=['Año'])
                result['Website'], result['Path'] = '', ''
                # result = years.merge(result, how='cross').sort_values(by=['Año']).reset_index(drop=True)
                result = range.merge(result, how='cross').rename(columns={'Date':'Fecha'}).sort_values(by=['Fecha']).reset_index(drop=True)
                results_df = pd.DataFrame()
                for group, df in result.groupby([result.Fecha.dt.year,result.Mercado]):
                    year, market = group[0], group[-1]
                    if market == 'diario':
                        df['Website'] = 'https://www.omie.es/es/file-access-list?parents=/Mercado%20Diario/1.%20Precios&dir=Precios%20horarios%20del%20mercado%20diario%20en%20Espa%C3%B1a&realdir=marginalpdbc'
                        df['Path']= f"{os.getcwd()}/Descargas/{market}/{year}".replace('\\', '/')
                    elif market == 'intradiario':
                        df['Website'] = 'https://www.omie.es/es/file-access-list?parents=/Mercado%20Intradiario/1.%20Precios&dir=Precios%20horarios%20del%20mercado%20intradiario%20de%20subastas%20en%20Espa%C3%B1a&realdir=marginalpibc'
                        df['Path']= f"{os.getcwd()}/Descargas/{market}/{year}".replace('\\', '/')
                    else:
                        df['Website'] = 'https://www.omie.es/es/file-access-list?parents=/Mercado%20Intradiario%20Continuo/1.%20Precios&dir=Precios%20m%C3%A1ximos%2C%20m%C3%ADnimos%20y%20medios%20ponderados%20para%20cada%20una%20de%20las%20horas%20en%20el%20mercado%20intradiario%20continuo&realdir=precios_pibcic'
                        df['Path'] = f"{os.getcwd()}/Descargas/{market}/{year}".replace('\\', '/')
                    results_df = pd.concat([results_df,df], axis=0).sort_values(by=['Fecha']).reset_index(drop=True)
                results_df.insert(1, 'Año', results_df['Fecha'].dt.year)
        return results_df

    @staticmethod
    def __request__(cls, url:Optional[str]='', 
                    a:bool =...,
                    certifacate:Optional[str]='',
                    password:Optional[str]=''):
        file = None
        try:
            if isinstance(url, str):
                file = requests.get(url, verify=False)
                file.raise_for_status()
                return file
        except requests.exceptions.HTTPError as error:
            if cls.print: print(error)
        except requests.exceptions.ConnectionError as error:
            if cls.print: print(error)
        except requests.exceptions.Timeout as error:
            if cls.print: print(error)
        except requests.exceptions.RequestException as error:
            if cls.print: print(error)
        return file


    def format_numbers_dates(series,save_format:str = 'CSV'):
        """ 
            1-. Dataframe use: Apply as DataFrame = DataFrame.apply(lambda x: format_numbers_dates(x,save_format))
            2-. Series use: series = format_numbers_dates(series,save_format)
                Use save_format: CSV to replace '.' to ',' and dates in %d/%m/%Y
                                DB to replace ',' to '.' and dates as %Y-%m-%d
                                EXCEL to replace ',' to '.' and dates as %Y-%m-%d
                            
        Args:
            series (pd.Series): Series to modify numbers / dates
            save_format (str, optional): Used to select the replacements to do. Possible values ['CSV','DB','EXCEL']. Defaults to 'CSV'.

        Returns:
            series: returns the series with the conversions
        """    
        save_format = save_format.upper()
        replacements = {
            'CSV':{ 'dates': '%d/%m/%Y',
                    'punctuation':','},
            
            'DB':{  'dates': '%Y-%m-%d',
                    'punctuation':'.'},
            
            'EXCEL':{'dates': '%Y-%m-%d',
                    'punctuation':'.'},
        }
        punctuation = replacements[save_format]['punctuation']
        date_saving_format = replacements[save_format]['dates']
        
        def date_formating(date): #Modulo para cambiar los formatos de fecha a uno solo %Y-%m-%d
            fecha = date
            fecha_formats_available =['%Y-%m-%d','%d/%m/%Y','%Y/%m/%d','%d-%m-%Y'] #Formato fechas que intenta hacerle el parse
            for date_format in fecha_formats_available:
                try:
                    fecha =  datetime.strptime(str(date), date_format).strftime(date_saving_format)
                    break
                except: 
                    pass
            return fecha
        
        #Cambiamos todos los numeros con ',' a '.' para conversion a float para los decimales
        mask_numeric = series.astype(str).str.strip('-').str.strip('+').str.replace(r'[,.]','',regex = True).str.isnumeric()
        series.loc[mask_numeric] = series.loc[mask_numeric].astype(str).str.replace(r'[,.]','.',regex = True)
        #Eliminamos aquellos numeros acabados en .0
        mask_zero_decimal = series.astype(str).str.strip('-').str.contains(r'[,.]0$','',regex = True)
        series.loc[mask_numeric & mask_zero_decimal] = series.loc[mask_numeric & mask_zero_decimal].str[:-2]
        #Solo ponemos 6 decimales
        mask_six_decimals = series.astype(str).str.contains(r'\.[0-9]{7,}$',regex = True)
        series.loc[mask_numeric & mask_six_decimals] = series.loc[mask_numeric & mask_six_decimals].astype(float).round(6).map('{:.6f}'.format)
        #Cambiamos todos los numeros a comma o punto dependiendo del endpoint de la informacion (CSV = , ; DB = '.')
        mask_numeric = series.astype(str).str.strip('-').str.replace(r'[,.]','',regex = True).str.isnumeric()
        series.loc[mask_numeric] = series.loc[mask_numeric].astype(str).str.replace(r'[,.]',punctuation,regex = True)
        #Transformamos las fechas al estandar Americano (%Y-%m-%d)
        mask_date = ((series.astype(str).str.contains(r'[/-]',regex = True)) & (series.astype(str).str.len() == 10))
        series.loc[mask_date] = series.loc[mask_date].apply(lambda x: date_formating(x))
        return series


