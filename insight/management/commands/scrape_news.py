from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re

from insight.models import CoronaCase, region_codes, city_codes

class NewsParser:
    def __init__(self):
        self.failed = False
        pass

    def run(self):

        client = requests.session()
        page = requests.get("https://www.expressen.se/nyheter/sa-planerar-de-att-stoppa-coronaviruset/")
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        div = soup.find("div", {'class': 'factbox__content'})
        ps = div.findAll ('p', limit=None)
        assets = CoronaCase.objects.update(backup=True)
        total = 0

        for p in ps:
            if self.failed==True:
                break

            news_string = p.text
            if news_string.count(')') > 1:
                news = news_string.split(')', 1)
                news_1 = news[0] + ')'
                news_2 = news[1]
                total+=self.parse_case(news_1, total)
                total+=self.parse_case(news_2, total)

            else:
                total+=self.parse_case(news_string, total)

        #self.parse_case('350-352: Tre personer i region okänd har testat positivt. (10/3)', total)

        if self.failed == True:
            print('failed')
            CoronaCase.objects.filter(backup=False).delete()
        else:
            CoronaCase.objects.filter(backup=True).delete()


    def parse_case(self, news_string, total):
        try:
            infected = self.parse_news_string(news_string, total)
            text = self.get_text(news_string)
            region = self.search_region(text)
            date = self.get_date(news_string)
            corona_dict = {
                'date' : date,
                'region': region,
                'text': text,
                'infected': infected,
                'backup': False
            }
            coronacase = CoronaCase.objects.create(**corona_dict)
            return infected
        except Exception as e:
            print (e, news_string)
            print('Sammanlagt' in news_string)
            if 'Sammanlagt' not in news_string:
                self.failed = True
            return 0

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

        return '99'

    def get_text(self, news_string):
        text = news_string.split(' ', 1)[1]
        text = text.split('(', 1)[0]
        return text

    def parse_news_string(self, news_string, total):
        infected_case = news_string.split(' ', 1)[0]
        no_of_infected = self.parse_infected(infected_case) - total

        return no_of_infected

    def parse_infected(self, infected_case):

        if '-' in infected_case:
            tuple = infected_case.split('-')
            big = re.sub('[^0-9]','', tuple[1])
            small = re.sub('[^0-9]','', tuple[0])
            no = big
            amount = int(big)-int(small)+1
        else:
            no = re.sub('[^0-9]','', infected_case)
            amount = 1

        return int(no)


class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        np = NewsParser()
        np.run()
