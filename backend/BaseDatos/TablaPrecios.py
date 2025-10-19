from Librerias.lib import *
from Librerias.vars import *
from OMIE.PreciosOMIE import PrecioOMIE
from REE.UploadEsios import UploadESIOS


@dataclass
class Inputs:
    '''Inputs OBligatorios:
        - Begin: date with format correct -> str|datetime
        - end: date with format correct -> str|datetime
        - clase: election of type clase to use'''
    
    start: Optional[str|datetime] = "don't date format"
    end: Optional[str|datetime] = "don't date format"
    clase: str = '' 

class Admin(Inputs):

    @staticmethod
    def __checkout__(cls):
        bool=False
        files = pd.Series(glob.glob(f'{os.getcwd()}/Descargas/*', recursive=True)) #f'{os.getcwd()}/Descargas/**/*.zip
        if not files.empty:
            files = files.str.split('\\', expand=True)
            filedowloaded = pd.to_datetime(files[files.columns[-1]], format='%Y%m')
            RangeDate = FormatDate.Añadir_cambios_horarios(
                start = cls.start, 
                end=cls.end, 
                freq='MS'
                )
            missing_date = RangeDate[~RangeDate.Date.isin(filedowloaded)]
            if not missing_date.empty:
                cls.start_aux, cls.end_aux = missing_date.min().squeeze().to_pydatetime(), missing_date.max().squeeze().to_pydatetime()
                bool =True
        elif cls.warning: raise ValueError(f'No existen archivos descargados en la carpeta Descargas del proyecto')
        return bool

    def __init__(cls, start, end, clase,
                 print:bool = True,
                 warning: bool = True,
                 url:str='',
                 multiproccesing:Optional[bool]=False, 
                 search:Optional[list]=[],
                 markets:Optional[list]=['diario', 'intradiario']) -> None:
        
        super().__init__(start, end, clase)
        if isinstance(start, str) and isinstance(end, str):
            fomartdates = FormatDate(start=start, end=end) 
            cls.start, cls.end = fomartdates.start, fomartdates.end
        cls.print = print
        cls.warning = warning
        cls.url = url
        cls.multiproccesing = multiproccesing
        cls.search = search
        cls.markets = markets
        cls.mongo = mongoDB.connect_db(host='') 

    async def __TypeClass__(cls):
        if cls.print: print(f'{datetime.now()} Estamos elegiendo la clase que vamos a utilizar')
        if bool(re.search(r'(?i).*OMIE.*', cls.clase)):
            if cls.clase.startswith('uplo'):
                await PrecioOMIE.get_dowload_price(
                    start=cls.start, 
                    end=cls.end, 
                    multiproccesing=cls.multiproccesing, 
                    print=cls.print, 
                    warning=cls.warning)
            else:
                precios = await PrecioOMIE.get_precios(
                    cls.start,cls.end, 
                    warning=False, 
                    mercado=cls.markets
                ) 
                return precios
        elif bool(re.search(r'(?i).*uplo.*ESIOS.*', cls.clase)):
            if cls.clase.startswith('uplo'):
                if await Admin.__checkout__(cls):
                    #---------- Descargando informacion de la pagina ----------
                    Scrapping(
                            start=cls.start_aux, 
                            end=cls.end_aux, 
                            pagina='ESIOS', 
                            namefiles='liquicomun',
                            print=cls.print, 
                            warning=cls.warning
                    ).__extractall__()
                    
                #---------- Upload informacion de la pagina ----------
                await UploadESIOS(
                        start=cls.start, 
                        end=cls.end, 
                        print=cls.print, 
                        warning=cls.warning
                    ).get_upload(search=cls.search)
            else: a=0  #Aqui ponemos la funcion para traernos los precios de la base de datos 
                
async def get_all_prices(data):
    '''
    Atributos que recibe la clase Admin de manera obligatoria
        - start = datetime|str -> fecha obligatoria para el tratamiento de datos 
        - end = datetime|str -> fecha obligatoria para el tratamiento de datos 
        - clase = str -> ejecuta la clase para la funcionalidad que se desea hacer  [upload-OMIE, upload-ESIOS]
        Si ejecuta upload-ESIOS, tengo que buscar la manera de pasar el atributo serach en el front-end opar subir los archivos que se quieran Tratar'''
    admin_result = await Admin(start=data.desde, 
                            end=data.hasta, 
                            warning=True, 
                            clase=data.tipo, 
                            print=False,
                            markets=data.mercados #search=['prsec', 'prter'], mercados = ['diario', 'intra', 'continuo'] 
                                                        ).__TypeClass__()  # mongo='conect', multiproccesing=False #, print=True, warning=False
    # Verificar si el resultado de Admin es un DataFrame, si no, convertirlo
    if not isinstance(admin_result, pd.DataFrame):
        df = pd.DataFrame(admin_result)  # Convertir a DataFrame si no lo es
    else:
        df = admin_result  # Si ya es un DataFrame, asignarlo directamente
    df = df.rename(columns={'Precio Español': 'Precio_Español'})
    df.insert(1,'Mes', df['Fecha'].dt.month)
    df.insert(2,'Hora', df['Fecha'].dt.hour)
    df['Fecha'] = df['Fecha'].dt.strftime('%Y-%m-%d')
    return df