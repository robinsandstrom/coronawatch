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
        self.watch_list = list(CountryTracker.objects.all().distinct().values_list('country', flat=True))

        pass

    def run(self):
        tbody = self.get_tables()

        self.parse_countries(tbody[0])
        self.parse_total(tbody[1])

    def get_tables(self):

        page = requests.get('https://www.worldometers.info/coronavirus/')
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        table = soup.find("table", {'id': 'main_table_countries'})
        tbody = table.findAll("tbody")
        return tbody

    def parse_countries(self, t_countries):

        trs = t_countries.findAll('tr', limit=None)
        #0 Country name #1 Total cases #2 New #3 Deaths #4 New deaths
        for tr in trs:
            tr

    def parse_total(self, t_total):

        tds = t_total.find('tr').findAll('td')
        total_cases = int(re.sub('[^0-9]','', tds[1].text))
        new_cases = int(re.sub('[^0-9]','', tds[2].text))
        deaths = int(re.sub('[^0-9]','', tds[3].text))
        new_deaths = int(re.sub('[^0-9]','', tds[4].text))
        print(total_cases, new_cases, deaths, new_deaths)

class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = WomParser()
        np.run()
