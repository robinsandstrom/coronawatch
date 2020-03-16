from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import requests
import re
import json
import xlrd

from insight.models import CountryTracker
from itertools import accumulate
from collections import OrderedDict

from pprint import pprint

class ECDCReader:
    def __init__(self):
        self.watch_list = list(CountryTracker.objects.exclude(country='global').distinct().values_list('country', flat=True))
        print('Watching:', self.watch_list)
        pass

    def run(self):
        ws = self.load_covid_file()
        summary = self.get_summary(ws)
        summary =  self.accumulate_cases(summary)
        self.insert_cases(summary)


    def load_covid_file(self):
        filename = 'COVID-19-geographic-disbtribution-worldwide-2020-03-14'
        workbook = xlrd.open_workbook(filename+'.xls')
        worksheet = workbook.sheet_by_index(0)
        return worksheet

    def accumulate_cases(self, summary):
        for country, dates in summary.items():
            od = OrderedDict(sorted(dates.items()))
            total_cases = 0
            total_deaths = 0
            for key in od:
                total_cases+=od[key]['new_cases']
                total_deaths+=od[key]['new_deaths']
                summary[country][key]['total_cases']=total_cases
                summary[country][key]['total_deaths']=total_deaths

        return summary

    def get_summary(self, worksheet):
        dictionary = {}

        for country in self.watch_list:
            dictionary[country] = {}

        for row in range(1, worksheet.nrows):
            date = self.from_excel_date(int(worksheet.cell_value(row, 0)))
            country_name = worksheet.cell_value(row, 1)
            new_cases = int(worksheet.cell_value(row, 2))
            new_deaths = int(worksheet.cell_value(row, 3))
            if country_name in dictionary:
                dictionary[country_name][str(date)[0:10]] = {
                            'date': date,
                            'country': country_name,
                            'new_cases': new_cases,
                            'total_cases': 0,
                            'new_cases': new_cases,
                            'total_deaths': 0,
                            'new_deaths': new_deaths,
                }

        return(dictionary)

    def from_excel_date(self, excel_date):
        dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + excel_date - 2)
        return dt

    def insert_cases(self, summary):
        for country, dates in summary.items():
            for key in dates:
                tracking_dict = dates[key]
                self.insert_tracking_dict_in_db(tracking_dict)

    def insert_tracking_dict_in_db(self, tracking_dict):
        ct = CountryTracker.objects.get_or_create(date=tracking_dict['date'], country=tracking_dict['country'])[0]
        CountryTracker.objects.filter(pk=ct.id).update(**tracking_dict)


class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        ecdc = ECDCReader()
        ecdc.run()
