from django.http import HttpResponse
from django.shortcuts import render

import csv

def index(request):
    template = 'insight/home.html'
    data = []
    with open('insight/total.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            data_row = []
            for cell in row:
                data_row.append(float(cell))
            data.append(data_row)

    return render(request, template, context={'data': data})
