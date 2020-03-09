from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re

from insight.models import CoronaCase, region_codes, city_codes

class NewsParser:
    def __init__(self):
        pass

    def run(self):

        client = requests.session()
        page = requests.get("https://www.expressen.se/nyheter/skolor-stanger-efter-bekraftade-coronafall/")
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {'class': 'factbox__content'})
        ps = div.findAll ('p', limit=None)

        CoronaCase.objects.all().delete()
        total = 0
        for p in ps:
            try:
                news_string = p.text
            
                infected = self.parse_news_string(news_string)
                text = self.get_text(news_string)
                region = self.search_region(text)
                date = self.get_date(news_string)
                corona_dict = {
                    'date' : date,
                    'region': region,
                    'text': text,
                    'infected': infected
                }
                coronacase = CoronaCase.objects.create(**corona_dict)
                total+=infected
                #print(corona_dict)
            except:
                print(news_string)

    def get_date(self, news_string):
        date = news_string.split('(')[1]
        date = date.split(')')[0]
        my_date = date.split('/')
        day = my_date[0]
        month = my_date[1]

        insert_date = datetime.now()
        insert_date = insert_date.replace(month = int(month), day=int(day))
        return insert_date.date()


    def search_region(self, text):
        text = text.lower()

        for region_key, region_name in region_codes.items():

            if region_name.lower() in text:
                return region_key

        for city_key, city_name in city_codes.items():

            if city_name.lower() in text:
                return city_key[0:2]

        return None

    def get_text(self, news_string):
        text = news_string.split(' ', 1)[1]
        text = text.split('(', 1)[0]
        return text

    def parse_news_string(self, news_string):
        infected_case = news_string.split(' ', 1)[0]
        no_of_infected = self.parse_infected(infected_case)
        return no_of_infected

    def parse_infected(self, infected_case):
        if '-' in infected_case:
            tuple = infected_case.split('-')
            big = re.sub('[^0-9]','', tuple[1])
            small = re.sub('[^0-9]','', tuple[0])
            amount = int(big)-int(small)+1
        else:
            amount = 1
        return int(amount)


class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = NewsParser()
        np.run()
