from Librerias.lib import *
from Librerias.vars import *

@dataclass
class inputs:
    '''Inputs OBligatorios:
        - path: str with format correct -> it can not be empty
    '''
    path:str = ""

class Extractall(inputs):

    @staticmethod
    def __fisrtHeaders__(self, 
                         type:str,
                         search:list,
                         series = pd.Series,
                         call:bool=False) -> str|pd.Series:
        if not call:
            filename = self.path.split('\\')[-1].split('.')[0]
            [os.makedirs(i) for i in [self.path[:-4]] if not os.path.exists(i)] 
            return filename
        else:
            search =  '|'.join(search)
            series = series.filter(regex=f'(?i).*{search}.*', axis=0) if not type.startswith('r') else series.filter(regex=f'(?i).*^((?!{search}).)*$', axis=0)
            if not series.empty: series = series.reset_index(drop=True)
            elif self.warning: raise ValueError(f'No hay archivos: {search} en el {type}')
            return series

    @staticmethod 
    def __extraerZIP__(self, 
                       _zip:pd.Series) ->pd.Series:
        Archive(self.path).extractall(self.path[:-4])
        for i in _zip:
            if self.path.split('\\')[-2] in i:
                _fileZIP = zipfile.ZipFile(self.path[:-4] +'/' + i, "r") 
                Archive(self.path[:-4] +'/' + i).extractall(self.path[:-4])
                _zip = pd.Series(os.listdir(self.path[:-4]), index=os.listdir(self.path[:-4]))
        return _fileZIP, _zip

    def __zip__(self, 
                type:str,
                search:list=['all']):
        results = pd.Series()
        zipfilename = Extractall.__fisrtHeaders__(self, type=type, search=search)
        #------- Creamos el nombre del archivo pero sin la extensión ------
        _fileZIP = zipfile.ZipFile(self.path, "r")
        _zip = pd.Series(_fileZIP.namelist(), index = _fileZIP.namelist())
        if _zip.filter(regex=r'.zip', axis=0).any(): _fileZIP, _zip = Extractall.__extraerZIP__(self, _zip=_zip)
        if not 'all' in search: _zip = Extractall.__fisrtHeaders__(self, series=_zip, type=type, search=search, call=True)
        if not _zip.empty:
            if self.print: print(f'Se han extraído {len(_zip)} ficheros del {zipfilename}')
            _zip.apply(lambda fil: _fileZIP.extract(fil, self.path[:-4]) if not fil in self.path[:-4] else 0)
            results = pd.concat([results, _zip.reset_index(drop=True)], axis=0)
            if not results.empty: results = self.path[:-4] +'/' + results
        elif self.warning: raise ValueError(f'Do not have files inside the .zip: {zipfilename}')
        return results

    
    def __rar__(self,
                type:str,
                search:list=['all']):
        results = pd.Series()
        rarfilename = Extractall.__fisrtHeaders__(self, type=type, search=search)
        Archive(self.path).extractall(self.path[:-4])
        _rar = pd.Series(os.listdir(self.path[:-4]), index=os.listdir(self.path[:-4]))
        if not _rar.empty:
            if self.print: print(f'Se han extraído los ficheros del {rarfilename}')
            if not 'all' in search: _rar = Extractall.__fisrtHeaders__(self, type=type, search=search, series=_rar, call=True)
            if not _rar.empty: (self.path[:-4]+'/' + _rar).apply(lambda x: os.remove(x))
            results = pd.concat([results, pd.Series(os.listdir(self.path[:-4]))], axis=0).reset_index(drop=True)
            if not results.empty: results = self.path[:-4] +'/' + results
        elif self.warning: raise ValueError(f'Do not have files inside the .zip: {rarfilename}')
        return results

    def get_extratac(self, 
                     type:str|list,
                     search:str|list):
        results = pd.Series()
        if type != '':
            if isinstance(type, str): type = [type]
            if isinstance(search, str): search = [search]
            for ext in type: results = pd.concat([results, self.__zip__(type=ext, search=search) if ext.startswith('z') else self.__rar__(type=ext, search=search)], axis=0)
        elif self.warning: raise ValueError(f'No existe el tipo de archivo para descomprimir type: {type}')
        return results  
    
    def __init__(self,
                 path:str=...,
                 print:bool=False, warning:bool=False, 
                 date:Optional[str|datetime]=None,
                 *args, **kwargs) -> None:
        super().__init__(path)
        if date !=None: self.date = FormatDate(start=date).start
        self.print = print
        self.warning = warning
        self.args = args
        self.kwargs = kwargs