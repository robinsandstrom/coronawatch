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
        pass

    def run(self):
        page = requests.get('https://www.worldometers.info/coronavirus/')

        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        table = soup.find("table", {'id': 'main_table_countries'})
        tbody = table.findAll("tbody")

        t_countries = tbody[0]
        trs = t_countries.findAll('tr', limit=None)

        t_total = tbody[1]

        tds = t_total.find('tr').findAll('td')

        total_cases = int(re.sub('[^0-9]','', tds[1].text))
        new_cases = int(re.sub('[^0-9]','', tds[2].text))
        new_deaths = int(re.sub('[^0-9]','', tds[4].text))
        deaths = int(re.sub('[^0-9]','', tds[7].text))
        print(total_cases, new_cases, new_deaths, deaths)
        
class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = WomParser()
        np.run()
