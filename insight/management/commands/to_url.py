from django.core.management.base import BaseCommand, CommandError
from insight.models import CoronaCase, region_codes, city_codes


class Command(BaseCommand):
    #A command which takes a from_date as an input and then tries to put in all Intrabank rates into DB from that date

    def add_arguments(self, parser):
        pass
        #parser.add_argument('from_date', type=str, nargs='?', default=str(date.today()-timedelta(days=7)))

    def handle(self, *args, **options):
        cases = CoronaCase.objects.filter(source__isnull=False)
        for case in cases:
            case.url = case.source.url
            case.save()
