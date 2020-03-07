import csv

from insight.models import region_codes
from collections import OrderedDict

def load_csv():
    data = []
    with open('insight/total.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            data_row = []
            for cell in row:
                data_row.append(float(cell))
            data.append(data_row)
    return data

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
