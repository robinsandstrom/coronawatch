from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
import requests
import re
import json
import xlrd

from insight.models import CoronaCase, region_codes, city_codes
from itertools import accumulate
from collections import OrderedDict

from pprint import pprint

class HospitalReader:
    def __init__(self):
        pass

    def run(self):
        ws = self.load_fhm_file()
        self.get_cols(ws)

    def load_fhm_file(self):
        filename = 'FHM'
        workbook = xlrd.open_workbook(filename+'.xlsx')
        worksheet = workbook.sheet_by_index(0)
        return worksheet

    def get_cols(self, worksheet):
        skip_rows=[1,23,24]

        for row in range(1, 22):
            self.insert_row(worksheet, row, 'in_hospital_care')

        for row in range(24, 45):
            self.insert_row(worksheet, row, 'in_intensive_care')


    def insert_row(self, worksheet, row, case_type):

            region = worksheet.cell_value(row, 0)

            start = datetime.now().date()
            start = start.replace(day=11)

            for col in range(1, worksheet.ncols):

                val = worksheet.cell_value(row, col) or 0
                val = int(val)
                iv = ''
                if case_type == 'in_intensive_care':
                    iv = 'intensiv'

                region_dict = {
                                'date': start,
                                'region': self.search_region(region),
                                'text': str(val) + ' ' + iv + 'vårdas just nu på sjukhus i ' + region + '. (' + str(start)+')',
                                'backup': False,
                                'infected': val,
                                'case_type': case_type,
                                'source': None
                            }

                CoronaCase.objects.create(**region_dict)
                start+=timedelta(days=1)



    def search_region(self, text):
        text = text.lower()

        for region_key, region_name in region_codes.items():

            if region_name.lower() in text:
                return region_key

        for city_key, city_name in city_codes.items():

            if city_name.lower() in text:
                return city_key[0:2]

        return '00'

class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        hosp = HospitalReader()
        hosp.run()
