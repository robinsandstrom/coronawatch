from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
import bs4
import requests
import re
import json

from insight.models import Article, CoronaCase, CountryTracker
from insight.backend import populate_regional_data

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
        #self.parse_aftonbladet()
        self.parse_dn()



    def parse_aftonbladet(self):
        r = requests.get('https://tethys.aftonbladet.se/configurationdata/coronadata')
        list_of_cases = r.json()['workSheets']['sverige']['rows']
        summary = {}
        for case in list_of_cases:
            #print(case)
            d = case['date']
            region = case['region']
            if d in summary:
                summary[d][region]['new_cases'] += 1
                summary[d]['Sverige']['new_cases'] += 1
            else:

                summary[d] = {
                        'Stockholm': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Uppsala': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Sörmland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Östergötland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Jönköping': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Kronoberg': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Kalmar': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Gotland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Blekinge': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Skåne': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Halland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Västra Götaland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Värmland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Örebro': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Västmanland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Dalarna': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Gävleborg': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Västernorrland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Jämtland': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Västerbotten': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Norrbotten': {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        },
                        'Sverige' : {
                            'new_cases': 0,
                            'new_deaths': 0,
                            'in_hospital': 0,
                            'in_intensive_care': 0
                        }
                }

                summary[d][region]['new_cases'] = 1
                summary[d]['Sverige']['new_cases'] = 1



        dead_site = 'https://tethys.aftonbladet.se/configurationdata/coronaswedead'
        r = requests.get(dead_site)
        list_of_cases = r.json()['workSheets']['swedead']['rows']

        for case in list_of_cases:

            d = case['date']
            region = case['region']

            if d in summary:
                summary[d][region]['new_deaths'] += 1
                summary[d]['Sverige']['new_deaths'] += 1
            else:
                pass

        in_care_site = 'https://tethys.aftonbladet.se/configurationdata/coronaregion'
        r = requests.get(in_care_site)
        list_of_cases = r.json()['workSheets']['region']['rows']

        for case in list_of_cases:
            if case['inlagda-totalt'] != 'nan':
                summary[case['date']][case['region']]['in_hospital'] = int(case['inlagda-totalt'])
                summary[case['date']]['Sverige']['in_hospital'] += int(case['inlagda-totalt'])


            if case['varav-iva'] != 'nan':
                summary[case['date']][case['region']]['in_intensive_care'] = int(case['varav-iva'])
                summary[case['date']]['Sverige']['in_intensive_care'] += int(case['varav-iva'])


        region_accu = {
            'Stockholm': {'cases': 0, 'deaths': 0},
            'Uppsala': {'cases': 0, 'deaths': 0},
            'Sörmland': {'cases': 0, 'deaths': 0},
            'Östergötland': {'cases': 0, 'deaths': 0},
            'Jönköping': {'cases': 0, 'deaths': 0},
            'Kronoberg': {'cases': 0, 'deaths': 0},
            'Kalmar': {'cases': 0, 'deaths': 0},
            'Gotland': {'cases': 0, 'deaths': 0},
            'Blekinge': {'cases': 0, 'deaths': 0},
            'Skåne': {'cases': 0, 'deaths': 0},
            'Halland': {'cases': 0, 'deaths': 0},
            'Västra Götaland': {'cases': 0, 'deaths': 0},
            'Värmland': {'cases': 0, 'deaths': 0},
            'Örebro': {'cases': 0, 'deaths': 0},
            'Västmanland': {'cases': 0, 'deaths': 0},
            'Dalarna': {'cases': 0, 'deaths': 0},
            'Gävleborg': {'cases': 0, 'deaths': 0},
            'Västernorrland': {'cases': 0, 'deaths': 0},
            'Jämtland': {'cases': 0, 'deaths': 0},
            'Västerbotten': {'cases': 0, 'deaths': 0},
            'Norrbotten': {'cases': 0, 'deaths': 0},
            'Sverige': {'cases': 0, 'deaths': 0}
        }

        today = datetime.now().date()

        if str(today) in summary:
            for name, region in summary[str(today)].items():
                pprint(region)
                if region['in_hospital'] == 0:
                    region['in_hospital'] = summary[str(today-timedelta(days=1))][name]['in_hospital']

                if region['in_intensive_care'] == 0:
                    region['in_intensive_care'] = summary[str(today-timedelta(days=1))][name]['in_intensive_care']



        for date, regions in summary.items():

            for region, cases in regions.items():
                region_accu[region]['cases']+=cases['new_cases']
                region_accu[region]['deaths']+=cases['new_deaths']

                cases['date'] = date
                cases['country'] = region
                cases['total_cases'] = region_accu[region]['cases']
                cases['total_deaths'] = region_accu[region]['deaths']

                ct = CountryTracker.objects.get_or_create(date=cases['date'], country=cases['country'])[0]
                CountryTracker.objects.filter(id=ct.id).update(**cases)

        pprint(summary)

    def parse_dn(self):
        r = requests.get('https://api.quickshot-widgets.net/fields/1141')
        updated_string = r.json()['fields'][2]['value']
        date_string  = updated_string.split('Uppdaterad')[1]
        date_string  = date_string.split('den ')[1]
        date_string = date_string.split('.')[0]
        day = date_string.split('/')[0]
        month = date_string.split('/')[1]

        today = datetime.now().date()

        if str(today.day) == day and str(today.month) == month:
            print('its today')
        else:
            return

        list_of_regions = r.json()['fields'][3]['value']
        totalt_inlagda = 0
        total_iva = 0

        for region in list_of_regions:
            country = region['region']

            if country == 'Totalt':
                continue

            if country == 'Södermanland':
                country = 'Sörmland'

            in_hospital = int(region['INLAGDA*'])
            totalt_inlagda+=in_hospital

            in_intensive_care = int(region['VARAV IVA**'])
            total_iva+=in_intensive_care

            ct = CountryTracker.objects.get_or_create(date=today, country=country)[0]

            if in_hospital > ct.in_hospital:
                ct.in_hospital = in_hospital

            if in_intensive_care > ct.in_intensive_care:
                ct.in_intensive_care = in_intensive_care

            ct.save()

        ct = CountryTracker.objects.get_or_create(date=today, country='Sverige')[0]

        if totalt_inlagda > ct.in_hospital:
            ct.in_hospital = totalt_inlagda

        if total_iva > ct.in_intensive_care:
            ct.in_intensive_care = total_iva

        ct.save()

    #    for case in list_of_cases:

class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = NewsParser()
        np.run()
