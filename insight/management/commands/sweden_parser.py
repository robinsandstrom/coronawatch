from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
import bs4
import requests
import re
import json

from insight.models import Article, CoronaCase, CountryTracker
from insight.backend import populate_regional_data
from django.db.models import Sum

from pprint import pprint

hospitals = {
    'Alingsås': '14',
    'Bollnäs': '21',
    'Borås': '14',
    'Danderyd': '01',
    'Eksjö': '06',
    'Eskilstuna': '04',
    'Falun': '20',
    'Gävle': '21',
    'Halmstad': '13',
    'Helsingborg': '12',
    'Hudiksvall': '22',
    'Jönköping': '06',
    'K Huddinge IVA': '01',
    'K Solna BIVA': '01',
    'K Solna ECMO': '01',
    'K Solna IVA': '01',
    'K Solna TIVA': '01',
    'Kalix': '25',
    'Kalmar': '08',
    'Karlskoga': '18',
    'Karlskrona IVA': '10',
    'Karlstad': '17',
    'Kristianstad': '12',
    'Kungälv': '14',
    'Linköping IVA': '05',
    'Ljungby': '07',
    'Mora': '20',
    'Norrköping': '05',
    'Norrtälje': '01',
    'NU Trollhättan': '14',
    'Nyköping': '04',
    'St Göran': '01',
    'SU BIVA': '14',
    'SU CIVA': '14',
    'SU Mölndal': '14',
    'SU Östra': '14',
    'SU Östra Inf': '14',
    'Sundsvall': '22',
    'Sunderby': '25',
    'SUS Lund IVA': '12',
    'SUS Lund TIVA': '12',
    'SUS Malmö Inf': '12',
    'SÖS IVA': '01',
    'SÖS MIVA': '01',
    'Umeå IVA': '24',
    'Uppsala CIVA': '03',
    'Varberg': '13',
    'Värnamo': '06',
    'Västervik': '08',
    'Västerås': '19',
    'Växjö': '07',
    'Örebro IVA': '18',
    'Örnsköldsvik': '22',
}

hospital_codes = {
'Blekinge': ['37', '87'],
 'Dalarna': ['27', '41'],
 'Gotland': ['61'],
 'Gävleborg': ['46', '4', '44'],
 'Halland': ['29', '35'],
 'Jämtland': ['23'],
 'Jönköping': ['15', '14', '16'],
 'Kalmar': ['1', '3'],
 'Kronoberg': ['49', '36'],
 'Norrbotten': ['45', '70', '68', '48'],
 'Skåne': ['54', '10', '73', '30', '74', '75', '88', '24', '53'],
 'Stockholm': ['6',
               '43',
               '62',
               '72',
               '95',
               '42',
               '77',
               '9',
               '8',
               '7',
               '58',
               '5',
               '89'],
 'Sörmland': ['64', '57'],
 'Uppsala': ['55', '90', '56', '79', '78'],
 'Västra Götaland': ['39',
                 '28',
                 '52',
                 '34',
                 '92',
                 '31',
                 '33',
                 '59',
                 '19',
                 '22',
                 '20',
                 '18',
                 '21',
                 '86',
                 '38'],
 'Värmland': ['25', '17', '26'],
 'Västerbotten': ['71', '51', '47', '81'],
 'Västernorrland': ['32', '66', '67'],
 'Västmanland': ['65'],
 'Örebro': ['84', '85', '50', '83'],
 'Östergötland': ['91', '11', '82', '40', '12']
 }

class NewsParser:

    def __init__(self):
        pass

    def run(self):
        self.parse_aftonbladet()



    def parse_aftonbladet(self):
        r = requests.get('https://tethys.aftonbladet.se/configurationdata/coronaswenumbers')
        list_of_cases = r.json()['workSheets']['swe_numbers']['rows']
        summary = {}

        for case in list_of_cases:
            d = case['date']
            region = case['region']
            cases = int(case['confirmed'])
            deaths = int(case['dead'])

            case = {
                'date': d,
                'total_cases': cases,
                'total_deaths': deaths,
                'country': region,
            }

            ct = CountryTracker.objects.get_or_create(date=case['date'], country=case['country'])[0]
            ct_old = CountryTracker.objects.get_or_create(date=datetime.strptime(case['date'],'%Y-%m-%d')-timedelta(days=1), country=case['country'])[0]
            prev_day_c = ct_old.total_cases or 0
            prev_day_d = ct_old.total_deaths or 0

            case['new_cases']= cases - prev_day_c
            case['new_deaths']= deaths - prev_day_d

            CountryTracker.objects.filter(id=ct.id).update(**case)


        in_care_site = 'https://tethys.aftonbladet.se/configurationdata/coronaregion'
        r = requests.get(in_care_site)
        list_of_cases = r.json()['workSheets']['region']['rows']


        for case in list_of_cases:
            d = case['date']
            region = case['region']
            ct = CountryTracker.objects.get_or_create(date=d, country=region)[0]

            if case['inlagda-totalt'] != 'nan':
                ct.in_hospital = case['inlagda-totalt']

            if case['varav-iva'] != 'nan':
                ct.in_intensive_care = case['varav-iva']

            ct.save()

        all_cases = CountryTracker.objects.exclude(country='Sverige')

        date = datetime.strptime('2020-01-30', '%Y-%m-%d').date()

        while date <= datetime.now().date():
            daily_cases = all_cases.filter(date=date)
            new_cases = daily_cases.aggregate(Sum('new_cases'))['new_cases__sum'] or 0
            total_cases = daily_cases.aggregate(Sum('total_cases'))['total_cases__sum'] or 0
            new_deaths = daily_cases.aggregate(Sum('new_deaths'))['new_deaths__sum'] or 0
            total_deaths = daily_cases.aggregate(Sum('total_deaths'))['total_deaths__sum'] or 0
            ct = CountryTracker.objects.get_or_create(date=date, country='Sverige')[0]
            ct.new_cases = new_cases
            ct.total_cases = total_cases
            ct.new_deaths = new_deaths
            ct.total_deaths = total_deaths
            ct.save()
            date += timedelta(days=1)

        all_cases_today = CountryTracker.objects.filter(date=datetime.now().date())
        i=0
        for case in all_cases_today:
            previous_case = CountryTracker.objects.filter(country=case.country, date=case.date-timedelta(days=1))[0]
            if case.in_hospital == 0 or  case.in_hospital ==  None:
                case.in_hospital = previous_case.in_hospital
            if case.in_intensive_care == 0 or  case.in_intensive_care ==  None:
                case.in_intensive_care = previous_case.in_intensive_care
            case.save()






class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = NewsParser()
        np.run()
