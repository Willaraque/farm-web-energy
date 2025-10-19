try:
    from Librerias.lib import *
    from Librerias.vars import *
except:
    import re,os,sys
    script_path = re.sub(r"[\\]","/",os.getcwd())
    sys.path.insert(0,script_path)
    from Librerias.lib import *
    from Librerias.vars  import *

@dataclass
class InputsData:
    '''Inputs OBligatorios:
        - Begin: date with format correct -> str|datetime
        - end: date with format correct -> str|datetime'''
    start:str|datetime = "don't date format"
    end: str|datetime = "don't date format"
    url:str = ''

class Scrapping(InputsData):

    def __options__(self):
        opts = Options()
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    def __driver__(self):
        driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()),
                                  options = self.__options__())
        return driver
    
    def __maximizar_window__(self, driver):
        driver.maximize_window()

    def __Cookies__(self, driver, wait):
        # driver.implicitly_wait(5)
        time.sleep(wait)
        driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()

    def __clickDate__(self, driver, wait, data):
        for idx in [1,2]:
            time.sleep(wait)
            driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').click()
            time.sleep(wait)
            # driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').send_keys(Keys.SHIFT, Keys.ARROW_UP)
            driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').send_keys(Keys.CONTROL,"a",Keys.DELETE)
            # driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').send_keys(Keys.DELETE)
            time.sleep(wait)
            driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').click()
            time.sleep(wait)
            if idx==1: 
                begin = data['Begin'].squeeze().strftime('%d / %m / %Y')
                driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').send_keys(begin)
            else: 
                end = data['End'].squeeze().strftime('%d / %m / %Y')
                driver.find_element(By.XPATH, f'//*[@id="datepicker{idx}"]').send_keys(end)

    def __clickSearch__(self, driver, wait, 
                        search:str='liquicomun', 
                        call:int=0):
        if call !=0 and bool(search):
            driver.find_element(By.XPATH, '//*[@id="esios-main-page"]/div/div[1]/div[2]/div[1]/input').click()
            time.sleep(wait)
            driver.find_element(By.XPATH, '//*[@id="esios-main-page"]/div/div[1]/div[2]/div[1]/input').send_keys(search)
            time.sleep(wait)
        else:
            time.sleep(wait)
            driver.find_element(By.XPATH, '//*[@id="tableDownloadJSONBtn"]').click()
            time.sleep(wait+1)


    def __dowload__(self, series, path):
        series_link = pd.DataFrame(tuple(series.filter(regex=r'(?i).*Docum.*', axis=0).values), columns=['name', 'url'])
        if not bool(re.search(r'(?i).*no se encontra.*', series_link.name.squeeze())):
            date = pd.DataFrame(tuple(series.filter(regex=r'(?i).*Fecha.*', axis=0).values), columns=['date', 'None'])['date'].squeeze()
            month = FormatDate(date=date.split(' ')[0]).date.strftime('%Y%m')
            path_month = f'{path}/{month}'
            [os.makedirs(i) for i in [path_month] if not os.path.exists(i)]
            name_file, url = series_link['name'].squeeze(), series_link['url'].squeeze()
            if bool(re.search(r'(?i).*liquicomun.*', name_file)):
                try: urllib.request.urlretrieve(url, f"{path_month}/{name_file}.zip") #Descarga la información y lo deja en al carpeta que vosotros querais
                except: 
                    if self.warning: print(f'name:{name_file}, Status:500, message: Internal server error')
                    pass
        elif self.warning: print(f'name:{name_file} No se encontraron resultados')

    def __finishSeccion__(self, driver):
        driver.close()
        driver.quit()

    def __completMonth__(self, desde, hasta):
        self.start = desde.replace(day=1)
        self.end = hasta.replace(day = calendar.monthrange(hasta.year,hasta.month)[-1])

    def __extractall__(self):
        wait = 1

        #------- Conexiones a la pagina a la cual vamos a extraer datos ----------
        driver = self.__driver__()
        driver.get(self.url)

        #-------- Maximizamos la venta del navegador y quitar las cookies
        self.__maximizar_window__(driver)
        self.__Cookies__(driver=driver, wait=wait)

        self.__completMonth__(desde=self.start, hasta=self.end)
        Dates = FormatDate.Añadir_cambios_horarios(start = self.start, end=self.end, freq='M').rename(columns={'Date':'End'})
        Dates['Begin'] = [i.replace(day=1) for i in Dates['End']]
        for group, df in Dates.groupby(['Begin', 'End']):
            #------- Primer y Segundo click para cambiar la fecha de busqueda
            self.__clickDate__(driver=driver, wait=wait, data=df)

            #----- Hacemos click para la busqueda del rango de fecha 
            self.__clickSearch__(driver=driver, wait=wait)

            #---------- Colocamos el filtro de Liquicomun (están los precios) ---------------
            for search in self.namefiles:
                self.__clickSearch__(driver=driver, wait=wait, search=search, call=1)

                #----- Buscamos los archivos para descargalos --------------------
                html = driver.page_source
                pd_html = pd.read_html(html, match=r'(?i).*Documento.*', extract_links='all')
                if bool(pd_html):
                    table = pd.DataFrame()
                    for i in pd_html:  table= pd.concat([table, i], axis=0)
                    if not table.empty:
                        path_dowload = f'{os.getcwd()}/Descargas'
                        [os.makedirs(i) for i in [path_dowload] if not os.path.exists(i)] #Creamos el directorio de Descarga de los Zips
                        table.filter(regex='(?i).*Documen|fecha.*', axis=1).apply(lambda x: self.__dowload__(series=x, path=path_dowload), axis=1)
                    elif Scrapping.warning: raise ValueError(f'Error al traer los datos de la tabla html')
                elif Scrapping.warning: raise ValueError(f'No hay información en la pagina Esios, para descargar datos')
        self.__finishSeccion__(driver=driver)
    
    def __init__(self, start, end, 
                 pagina:str = '', url:str='',
                 namefiles:str|list='liquicomun',
                 print:bool=False, warning:bool=False, 
                 date:Optional[str|datetime]=None,
                 *args, **kwargs) -> None:
        super().__init__(start, end, url)
        dates = FormatDate(start= start, end=end)
        if bool(dates): self.start, self.end = dates.start, dates.end
        if pagina.startswith('ESI'): url = 'https://www.esios.ree.es/es/descargas?date_type=publicacion&start_date=20-04-2024&end_date=20-04-2024'
        else: raise ValueError('Pasar obligatoriamente la URL de la pagina para hacer el Scrapping')
        self.url = url
        self.namefiles = [str(i).strip().lower() for i in namefiles] if isinstance(namefiles, list) else [str(namefiles).strip().lower()] 
        self.print = print
        self.warning = warning
        self.args = args
        self.kwargs = kwargs