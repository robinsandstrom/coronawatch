from collections import OrderedDict
from openpyxl import Workbook
from insight.models import CoronaCase, region_codes
from datetime import datetime, timedelta
from insight.backend import aggregate_by_dates

def get_excel_file():
    wb = Workbook()
    wb.active = 0
    ws = wb.active
    ws.title = 'COVID-19-geographic-distributi'


    setHeader(ws)
    setData(ws)

    return wb

def setHeader(ws):
    headers = ['DateRep', 'Day', 'Month', 'Year', 'Cases', 'Deaths', 'Countries and territories', 'GeoId', 'IC']
    for ix in range(1, len(headers)+1):
        _ = ws.cell(column=ix, row=1, value=headers[ix-1])

def setData(ws):
    cases = CoronaCase.objects.all()
    rd = parse_for_excel(cases)
    ix = 2
    for key, value in sorted(rd.items(), key=lambda item: region_codes[item[0]]):
        for str_date, dict in sorted(value.items(), key=lambda item: item[0], reverse=True):
            date = datetime.strptime(str_date, '%Y-%m-%d')
            _ = ws.cell(column=1, row=ix, value=excel_date(date))
            _ = ws.cell(column=2, row=ix, value=date.day)
            _ = ws.cell(column=3, row=ix, value=date.month)
            _ = ws.cell(column=4, row=ix, value=date.year)
            _ = ws.cell(column=5, row=ix, value=dict.get('confirmed'))
            _ = ws.cell(column=6, row=ix, value=dict.get('death'))
            _ = ws.cell(column=7, row=ix, value=region_codes[key])
            _ = ws.cell(column=8, row=ix, value=key)
            _ = ws.cell(column=9, row=ix, value=dict.get('intensive_care'))
            ix+=1

def parse_for_excel(cases):
    regional_data = {}

    for c in region_codes:
        r_cases = cases.filter(region=c)
        regional_data[c] = aggregate_by_dates(r_cases, days=365)

    return regional_data

def excel_date(date1):
    temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)
