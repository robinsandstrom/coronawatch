from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re
import json

from insight.models import CountryTracker

from pprint import pprint

class WomParser:
    def __init__(self):
        self.watch_list = list(CountryTracker.objects.exclude(country='global').distinct().values_list('country', flat=True))
        print('Watching:', self.watch_list)
        pass

    def run(self):
        tbody = self.get_tables()

        self.parse_countries(tbody[0])
        self.parse_total(tbody[1])

    def get_tables(self):

        page = requests.get('http://www.worldometers.info/coronavirus/')
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        table = soup.find("table", {'id': 'main_table_countries_today'})
        tbody = table.findAll("tbody")
        return tbody

    def parse_countries(self, t_countries):

        trs = t_countries.findAll('tr', limit=None)

        for tr in trs:

            tds = tr.findAll('td')
            country = tds[0].text.replace(' ', '', 2)
            if country in self.watch_list:
                tracking_dict = self.get_tracking_dict(tds, country)
                if tracking_dict:
                    self.insert_tracking_dict_in_db(tracking_dict)

    def parse_total(self, t_total):

        tr = t_total.find('tr')
        tds = tr.findAll('td')
        tracking_dict = self.get_tracking_dict(tds, 'Global')

        self.insert_tracking_dict_in_db(tracking_dict)


    def get_tracking_dict(self, tds, country):

        try:
            total_cases = int(re.sub('[^0-9]','', tds[1].text))
        except:
            total_cases = 0

        try:
            new_cases = int(re.sub('[^0-9]','', tds[2].text))
        except:
            new_cases = 0

        try:
            deaths = int(re.sub('[^0-9]','', tds[3].text))
        except:
            deaths = 0

        try:
            new_deaths = int(re.sub('[^0-9]','', tds[4].text))
        except:
            new_deaths = 0

        return {
                    'total_cases' : total_cases,
                    'new_cases' : new_cases,
                    'total_deaths' : deaths,
                    'new_deaths' : new_deaths,
                    'country': country,
                    'date': datetime.now().date()
                    }


    def insert_tracking_dict_in_db(self, tracking_dict):
        ct = CountryTracker.objects.get_or_create(date=tracking_dict['date'], country=tracking_dict['country'])[0]
        CountryTracker.objects.filter(pk=ct.id).update(**tracking_dict)

class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = WomParser()
        np.run()
