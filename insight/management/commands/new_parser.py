from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import bs4
import requests
import re
import json

from insight.models import Article, CoronaCase, region_codes, city_codes, ScrapeSite, Source
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
 'V. Götaland': ['39',
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

        try:
            self.parse_omni()
        except:
            print('Failed Omni')

        try:
            self.parse_sir()
        except:
            pass

    def parse_omni(self):
        url = 'https://omni-content.omni.news/articles?topics=3ee2d7f6-56f1-4573-82b9-a4164cbdc902'
        r = requests.get(url)
        articles = r.json()['articles']
        for article in articles:

            article_dict = {
                    'title': article[0]['title']['value'],
                    'text' : article[0]['main_text']['paragraphs'][0]['text']['value'],
                    'active': True
                    }

            a = Article.objects.get_or_create(**article_dict)[0]
            source_url = 'https://omni.se/a/' + article[0]['article_id']
            s = Source.objects.get_or_create(article=a, url=source_url)




    def parse_sir(self):
        site = ScrapeSite.objects.get(name='Svenska Intensivvårdsregistret')
        url = site.url
        for key, value in hospital_codes.items():
            payload = {
                'highChartUrl': '/api/reports/GenerateHighChart',
                'tableUrl': 'value2',
                'chartWidth': 900,
                'reportName': 'vtfstart-corona',
                'startdat': '2020-01-01',
                'stopdat': str(datetime.now().date()),
                'sasong[0]': '2019'
                }
            for j in range(len(value)):
                payload['avd['+str(j)+']']=value[j]

            r = requests.get(url)
            r = requests.post(url, data=payload)
            intensive_care_cases = r.json()['ChartSeries']

            region_code = self.search_region(key)

            if len(intensive_care_cases) > 0:
                data = intensive_care_cases[0]['Data']
                for d in data:
                    date = datetime.strptime(d['Name'], '%Y-%m-%d %H:%M:%S').date()
                    infe = int(d['Value'])
                    c = CoronaCase.objects.get_or_create(region=region_code, date=date, case_type='intensive_care')[0]
                    print('Inserted for', key)
                    c.infected = infe
                    c.source = site
                    c.text = 'nytt intensivvårdsfall'
                    c.save()




    def parse_svt(self):

        site = ScrapeSite.objects.get(name='SVT')
        r = requests.get(site.url)
        summary = r.json()['data']
        self.add_cases_from_summary(summary, site)

        for reg in summary:
            reg['antal'] = reg['dead']

        self.add_cases_from_summary(summary, site, case_type='death')

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

    def add_cases_from_summary(self, summary, site, case_type='confirmed'):

        cases = CoronaCase.objects.filter(case_type=case_type)
        ord, regional_data = populate_regional_data(cases)

        if (type(summary)) is dict:
            summary = summary.values()

        for region_dict in summary:

            region_code = region_dict['kod']
            current_value = region_dict['antal']
            previous_value = regional_data[region_code][case_type]

            if current_value > previous_value:
                infected = current_value - previous_value
                self.add_new_case(infected, region_code, case_type, source=site)

    def add_new_case(self, infected, region, case_type, source=None):
        date = datetime.now().date()
        infected = int(infected)

        if infected == 1:
            ny = 'nytt'
        else:
            ny = 'nya'

        if case_type=='confirmed':
            text = str(infected) + ' ' + ny + ' fall i ' + region_codes[region]

        elif case_type=='intensive_care':
            text = str(infected) + ' ' + ny + ' intensivvårdsfall i ' + region_codes[region]

        elif case_type=='death':
            text = str(infected) + ' ' + ny + ' dödsfall i ' + region_codes[region]



        if infected > 0:

            corona_dict = {
                'date' : date,
                'region': region,
                'text': text,
                'infected': infected,
                'backup': False,
                'case_type': case_type,
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
