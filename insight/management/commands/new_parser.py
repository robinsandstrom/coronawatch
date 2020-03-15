from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re
import json

from insight.models import CoronaCase, region_codes, city_codes, ScrapeSite
from insight.backend import populate_regional_data

from pprint import pprint

class NewsParser:

    def __init__(self):
        pass

    def run(self):
        try:
            self.parse_svt()
        except:
            print('Failed SVT')

        try:
            self.parse_expressen()
        except:
            print('Failed Expressen')

        try:
            self.parse_aftonbladet()
        except:
            print('Failed Aftonbladet')

        try:
            self.parse_fhm()
        except:
            print('Failed FHM')

    def parse_svt(self):

        site = ScrapeSite.objects.get(name='SVT')
        r = requests.get(site.url)
        summary = r.json()['data']

        self.add_cases_from_summary(summary, site)

    def parse_expressen(self):

        site = ScrapeSite.objects.get(name='Expressen')
        ps = self.get_expressen_paragraphs(site)
        summary = self.expressen_to_summary(ps)

        self.add_cases_from_summary(summary, site)

    def parse_aftonbladet(self):
        site = ScrapeSite.objects.get(name='Aftonbladet')
        r = requests.get(site.url)
        list_of_cases = r.json()['workSheets']['sverige']['rows']
        summary = self.aftonhoran_to_summary(list_of_cases)

        self.add_cases_from_summary(summary, site)

    def parse_fhm(self):
        site = ScrapeSite.objects.get(name='Folkhälsomyndigheten')
        trs = self.get_fhm_tds(site)
        summary = self.fhm_to_summary(trs)
        pprint(summary)
        self.add_cases_from_summary(summary, site)

    def aftonhoran_to_summary(self, list_of_cases):
        regional_summary = {}

        for l in list_of_cases:
            region_name = l['region']
            if region_name in regional_summary:
                regional_summary[region_name]+=1
            else:
                regional_summary[region_name]=1

        parsed_list = []

        for region, infected in regional_summary.items():

            region_dict = {
                        'kod': self.search_region(region),
                        'namn': region,
                        'antal': infected,
            }

            parsed_list.append(region_dict)

        return parsed_list

    def fhm_to_summary(self, trs):
        parsed_data = []
        for tr in trs:
            tds = tr.findAll('td')
            try:
                region = self.search_region(tds[0].text)
                value = int(tds[1].text)
            except:
                pass
            else:
                region_dict = {'kod': region, 'antal': value, 'namn': region_codes[region]}
                parsed_data.append(region_dict)

        return parsed_data

    def get_fhm_tds(self, site):
        url = site.url
        page = requests.get(url)

        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {'id': 'content-primary'})
        table = div.findAll("table")[0]
        tbody = table.find("tbody")
        trs = tbody.findAll('tr', limit=None)
        return trs[:-1]

    def expressen_to_summary(self, ps):
        parsed_data = []
        for p in ps:

            text = p.text

            if 'Sammanlagt' in text or 'Uppdaterad' in text or len(text)<5:
                continue
            try:
                region = self.search_region(text)
            except:
                pass
            else:
                value = int(re.sub('[^0-9]','', text.split(' ')[0]))
                region_dict = {'kod': region, 'antal': value, 'namn': region_codes[region]}
                parsed_data.append(region_dict)

        return parsed_data

    def add_cases_from_summary(self, summary, site):

        cases = CoronaCase.objects.all()
        ord, regional_data = populate_regional_data(cases)

        for region_dict in summary:

            region_code = region_dict['kod']
            current_value = region_dict['antal']
            previous_value = regional_data[region_code]['value']

            if current_value != previous_value:
                infected = current_value - previous_value
                self.add_new_case(infected, region_code, site)

    def add_new_case(self, infected, region, source=None):
        date = datetime.now().date()

        if infected == 1:
            ny = 'nytt'
        else:
            ny = 'nya'

        text = str(infected) + ' ' + ny + ' fall i ' + region_codes[region]

        if infected > 0:

            corona_dict = {
                'date' : date,
                'region': region,
                'text': text,
                'infected': infected,
                'backup': False,
                'case_type': 'confirmed',
                'source': source
            }

            CoronaCase.objects.create(**corona_dict)

    def get_expressen_paragraphs(self, site):
        url = site.url
        page = requests.get(url)

        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {'class': 'factbox__content'})
        ps = div.findAll ('p', limit=None)
        return ps

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
        np = NewsParser()
        np.run()
