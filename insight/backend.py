import csv

from insight.models import region_codes
from collections import OrderedDict
from datetime import datetime, timedelta

def load_csv():
    data = []
    with open('insight/total.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            data_row = []
            for cell in row:
                data_row.append(float(cell))
            data.append(data_row)

    avg_row = get_avg_row(data)
    swe_and_avg = [data[8], avg_row]
    return data, swe_and_avg

def get_avg_row(data):
    avgarr = []
    for j in range(1, len(data[0])):
        avg = 0
        den = 0
        for i in range(1, 8):
            if data[i][j] > 0:
                avg+= data[i][j]
                den+=1
        if den>0:
            avg = avg/den
        avgarr.append(int(avg))
    return avgarr

def aggregate_by_dates(cases):
    date_from = datetime.now()
    agg_by_dates = OrderedDict()
    for case in cases.filter(date__gte=(date_from-timedelta(days=31))).order_by('date'):
        if str(case.date) in agg_by_dates:
            agg_by_dates[str(case.date)]+=case.infected
        else:
            agg_by_dates[str(case.date)] = case.infected

    return agg_by_dates

def populate_regional_data(cases):
    regional_data = {}
    for i in range(1, 26):
        j = str(i)
        if len(j) == 1:
            j = '0' + j

        if i not in [2, 11, 15, 16]:
            regional_data[j] = {
                    'region': region_codes[j],
                    'value': 0
            }

    for case in cases:
        j = str(case.region)
        if len(j) == 1:
            j = '0' + j
        regional_data[j]['value'] += case.infected

    return OrderedDict(sorted(regional_data.items(), key = lambda t: t[1]['value'], reverse=True)), regional_data

def get_total(cases):
    total = 0

    for case in cases:
        total+=case.infected

    return total

def get_new_cases(cases):
    date_from = datetime.now()
    new_cases = cases.filter(date__gte=date_from)
    return new_cases
