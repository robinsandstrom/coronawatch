from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re

from insight.models import CoronaCase, region_codes, city_codes
from insight.backend import populate_regional_data

from pprint import pprint

class NewsParser:
    def __init__(self):
        self.failed = False
        pass

    def run(self):

        client = requests.session()
        page = requests.get("https://www.expressen.se/nyheter/sa-planerar-de-att-stoppa-coronaviruset/")
        page2 = "https://www.svt.se/datajournalistik/har-sprider-sig-coronaviruset/"
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {'class': 'factbox__content'})
        ps = div.findAll ('p', limit=None)
        cases = CoronaCase.objects.all()
        ordered_regional_data, regional_data = populate_regional_data(cases)

        for p in ps:
            text = p.text
            if 'Sammanlagt' not in text and 'Uppdaterad' not in text:

                region = self.search_region(text)
                current_value = int(re.sub('[^0-9]','', text.split(' ')[0]))
                previous_value = regional_data[region]['value']

                if current_value != previous_value:

                    infected = current_value - previous_value
                    region = region
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
                            'backup': False
                        }

                        CoronaCase.objects.create(**corona_dict)


    def search_region(self, text):
        text = text.lower()

        for region_key, region_name in region_codes.items():

            if region_name.lower() in text:
                return region_key

        for city_key, city_name in city_codes.items():

            if city_name.lower() in text:
                return city_key[0:2]

        return '99'

class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = NewsParser()
        np.run()
