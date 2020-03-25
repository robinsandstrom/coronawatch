import csv

from insight.models import region_codes
from collections import OrderedDict
from datetime import datetime, timedelta

population_by_regions = {
    'Blekinge': 159606,
    'Dalarna': 287966,
    'Gotland': 59686,
    'Gävleborg': 287382,
    'Halland': 333848,
    'Jämtland': 130810,
    'Jönköping': 363599,
    'Kalmar': 245446,
    'Kronoberg': 201469,
    'Norrbotten': 250093,
    'Skåne': 1377827,
    'Stockholm': 2377081,
    'Södermanland': 297540,
    'Uppsala': 383713,
    'Värmland': 282414,
    'Västerbotten': 271736,
    'Västernorrland': 245347,
    'Västmanland': 275845,
    'Västra Götaland': 1725881,
    'Örebro': 304805,
    'Östergötland': 465495,
    'Okänd region': 100000000
}

def load_csv():
    data = []
    with open('total.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            data_row = []
            j = 0
            for cell in row:
                if j > 0:
                    data_row.append(float(cell))
                j+=1
            data.append(data_row)

    avg_row = get_avg_row(data)
    swe_and_avg = [data[9], avg_row]
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

def aggregate_by_dates(cases, days=31):
    date_from = datetime.now()
    agg_by_dates = OrderedDict()
    for case in cases.filter(date__gte=(date_from-timedelta(days=days))).order_by('date'):
        if str(case.date) in agg_by_dates:
            agg_by_dates[str(case.date)][case.case_type]+=case.infected
        else:
            agg_by_dates[str(case.date)] = {
                            'confirmed': 0,
                            'death': 0,
                            'intensive_care': 0
            }
            agg_by_dates[str(case.date)][case.case_type] = case.infected

    return agg_by_dates

def populate_regional_data(cases):

    key_figures = {
        'confirmed': 0,
        'intensive_care': 0,
        'death': 0,
        'new_confirmed': 0,
        'new_intensive_care': 0,
        'new_death': 0
    }

    today = datetime.now().date()



    regional_data = {}
    regional_data['00'] = {
            'region': region_codes['00'],
            'confirmed': 0,
            'death': 0,
            'intensive_care': 0,
        }
    for i in range(1, 26):
        j = str(i)
        if len(j) == 1:
            j = '0' + j

        if i not in [2, 11, 15, 16]:
            regional_data[j] = {
                    'region': region_codes[j],
                    'confirmed': 0,
                    'death': 0,
                    'intensive_care': 0,
            }

    for case in cases:
        j = str(case.region)
        if len(j) == 1:
            j = '0' + j
        if j in regional_data:
            regional_data[j][case.case_type] += case.infected
            key_figures[case.case_type] += case.infected
            if case.date >= today:
                key_figures['new_'+case.case_type] += case.infected
        else:
            regional_data[j] = {
                    'region': region_codes[j],
                    'confirmed': 0,
                    'death': 0,
                    'intensive_care': 0,
                    'per_capita': 0
                    }
            regional_data[j][case.case_type] = case.infected

    for regional in regional_data:
        regional_data[regional]['per_capita'] = int(100000 * regional_data[regional]['confirmed']/population_by_regions[regional_data[regional]['region']])

    return OrderedDict(sorted(regional_data.items(), key = lambda t: t[1]['confirmed'], reverse=True)), regional_data, key_figures
