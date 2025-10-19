from Librerias.lib import *
from Librerias.vars import *

@dataclass
class InputsDate:
    '''Inputs OBligatorios:
        - Begin: date with format correct -> str|datetime
        - end: date with format correct -> str|datetime'''
    start:str|datetime = "don't date format"
    end: str|datetime = "don't date format"


class FormatDate(InputsDate):

    @staticmethod
    def decorator_date(fuction):
        @functools.wraps(fuction)
        def wrapps(*args, **kwargs):
            self_input = args
            if bool(self_input): return fuction(*args, **kwargs)
        return wrapps

    @decorator_date
    def __validation_date__(self, 
                            date:Optional[str|datetime]=None,
                            start:Optional[str|datetime]=None, 
                            end:Optional[str|datetime]=None):
        '''Estamos conviertiendo la fecha en formato datetime'''
        if start !=None: self.start = self.fecha_to_datetime(start)
        if end !=None: self.end = self.fecha_to_datetime(end)
        if date !=None:  self.date = self.fecha_to_datetime(date)

    def fecha_to_datetime(self, date):
        if isinstance(date,str):
            #Formato fechas que intenta hacerle el parse
            fecha_formats_available = ['%Y-%m-%d','%d/%m/%Y','%d/%m/%y','%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S','%Y/%m/%d','%d-%m-%Y', '%Y-%m-%dT%H:%M'] 
            for date_format in fecha_formats_available:
                try:
                    date =  datetime.strptime(date, date_format)
                    break
                except: pass
        return date

    @staticmethod
    def Change_Hour_Dates(self, dates_range):
        changing_hours_dates = []
        date_column = dates_range.name
        Dates = dates_range.to_frame()
        years = Dates[date_column].dt.year.unique().tolist()
        for year in years:
            for month in [3,10]:
                start_month = datetime(year,month,1)
                end_month = start_month.replace(day = calendar.monthrange(start_month.year,start_month.month)[-1])
                month_range = pd.date_range(start = start_month, end = end_month, freq= 'D').to_frame(name='Date').reset_index(drop=True)
                month_range['weekday'] = month_range['Date'].dt.day_of_week
                last_sunday_month = month_range['Date'][month_range['weekday'] == 6].iloc[-1].to_pydatetime()
                changing_hours_dates.append(last_sunday_month)
        return changing_hours_dates
    
    @staticmethod
    def __as_pdData__(self, start, 
                      end, freq)->pd.DataFrame:
        mask_formatDate = start !=None and end != None
        if mask_formatDate:
            return pd.date_range(start=start, end=end, freq=freq).to_frame(name='Date').reset_index(drop=True)
        else: raise  ValueError('You need pass to date')

    @classmethod
    def Añadir_cambios_horarios(self, 
                                start:str|datetime = None, 
                                end:str|datetime = None,
                                freq:str='H'):
        #Pass to series
        dates_range = FormatDate.__as_pdData__(self, start, end, freq)
        dates_return = deepcopy(dates_range)
        if freq == 'H':
            dates = deepcopy(dates_range)
            if isinstance(dates_range, pd.DataFrame): dates = dates_range[dates_range.columns.values[0]]
            #Create the new date range with change hour
            list_change_hour = FormatDate.Change_Hour_Dates(self, dates)
            series_change_hour  = pd.Series(list_change_hour).apply(lambda x: x.replace(hour = 2))               
            mask_dates_add_drop = dates.isin(series_change_hour)
            dates_october = dates.loc[mask_dates_add_drop & (dates.dt.month == 10)]
            dates_march_index = dates.loc[mask_dates_add_drop & (dates.dt.month == 3)].index
            dates = dates.drop_duplicates(keep = 'first')
            dates_return = dates.drop(labels = dates_march_index)
            if len(dates_october)>0: dates_return = pd.concat([dates_return, dates_october], axis=0, join='outer').reset_index(drop=True)
            dates_return = dates_return.sort_values().reset_index(drop = True).to_frame(name = 'Date')
            #Create the season series
            series_march = series_change_hour.loc[series_change_hour.dt.month == 3].reset_index(drop = True)
            series_october = series_change_hour.loc[series_change_hour.dt.month == 10].reset_index(drop = True)
            summer_interval = pd.concat([series_march, series_october], axis = 1).rename(columns = {0:'march', 1:'october'})
            mask_summer_df = pd.DataFrame((summer_interval['march'][0] < dates_return['Date']) & (dates_return['Date'] < summer_interval['october'][0]))
            mask_summer = mask_summer_df.sum(axis = 1).apply(lambda boll_line: boll_line > 0)
            mask_october = dates_return['Date'].isin(series_change_hour) #Only get october bacause we delete march before
            first_2pm_hour_index = dates_return['Date'].loc[mask_october].drop_duplicates(keep = 'first').index
            dates_return.loc[mask_summer, 'Season'] = 1
            dates_return.loc[first_2pm_hour_index, 'Season'] = 1
            dates_return['Season'].fillna(0, inplace = True)
            dates_return = dates_return.rename(columns = {'Date':dates.name})
        return dates_return

    def corregir_horas_cest_madrid(self, series):
        cest = timezone("Europe/Madrid")
        hours_change = int(str(cest.localize(datetime.fromisoformat(str(series['datetime']))))[-4:-3])
        series['datetime'] = series['datetime'] + timedelta(hours = hours_change)
        return series
    
    def __init__(self,
                 date:str|datetime = None,
                 start:str|datetime = None,
                 end:str|datetime = None):
        super().__init__(start, end)
        FormatDate.__validation_date__(self, date, start, end)
        