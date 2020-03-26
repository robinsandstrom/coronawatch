from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data, aggregate_by_dates
from insight.models import Article, CoronaCase, CountryTracker
from datetime import datetime, timedelta
from collections import OrderedDict
from insight.management.commands.new_parser import NewsParser
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum
from insight.andre.SEQIJR import SEQIJR
from insight.andre.FileReader import FileReader
import json
from django.core.serializers.json import DjangoJSONEncoder
from insight.excel import get_excel_file
from django.db.models import Count
from django.db.models.functions import Trunc

def index(request):

    template = 'insight/home.html'
    articles = Article.objects.all().order_by('-time_created')[0:5]

    return render(request, template, context={
                                            'articles': articles,
                                            })

def about(request):
    template = 'insight/about.html'
    last_updated = CoronaCase.objects.all().first().time_created
    return render(request, template, context={
                                            'last_updated': last_updated,
                                            })

def modeling(request):
    template = 'insight/modeling.html'
    last_updated = CoronaCase.objects.all().order_by('time_created').last().time_created
    return render(request, template, context={
                                            'last_updated': last_updated,
                                            })
def update(request):
    np = NewsParser()
    np.run()
    return HttpResponse('updated')

def excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = 'COVID-19-geographic-distribution-sweden-' + str(datetime.now().date())+'.xlsx'
    response['Content-Disposition'] = 'attachment; filename='+ str(filename)
    wb = get_excel_file()
    wb.save(response)
    return response

def get_curve(request):

    N = float(request.GET.get('N', None))
    Pi = float(request.GET.get('pi', None))
    mu = 1 / (80 * 365)
    b = float(request.GET.get('b', None))
    e_E = float(request.GET.get('e_E', None))
    e_Q = float(request.GET.get('e_Q', None))
    e_J = float(request.GET.get('e_J', None))
    g_1 = float(request.GET.get('g_1', None))
    g_2 = float(request.GET.get('g_2', None))
    s_1 = float(request.GET.get('s_1', None))
    s_2 = float(request.GET.get('s_2', None))
    k_1 = float(request.GET.get('k_1', None))
    k_2 = float(request.GET.get('k_2', None))
    d_1 = float(request.GET.get('d_1', None))
    d_2 = float(request.GET.get('d_2', None))
    p_days = int(request.GET.get('p_days', None))
    country = request.GET.get('country', None)
    region = request.GET.get('region', None)

    if country != 'Sweden' or region == 'Sverige':
        covid19_filename = 'COVID-19-geographic-disbtribution-worldwide-2020-03-23.xlsx'
        population_filename = 'PopulationByCountry.xlsx'
        pop_getter = country
    else:
        covid19_filename = 'COVID-19-geographic-distribution-sweden-2020-03-24.xlsx'
        population_filename = 'PopulationBySwedishRegion.xlsx'
        pop_getter = region

    files = FileReader(covid19_filename, population_filename)
    N = N * files.population(pop_getter)

    model = SEQIJR(N, Pi, mu, b,
                    e_E, e_Q, e_J,
                    g_1, g_2,
                    s_1, s_2,
                    k_1, k_2,
                    d_1, d_2)

    data = model.calc(pop_getter, files, p_days)
    dump = json.dumps(data, indent=4, sort_keys=True, default=str)

    return HttpResponse(dump, content_type='application/json')


def get_numbers(request):

    region = request.GET.get('region', None)
    all_cases = CoronaCase.objects.all().order_by('date')

    if region is not None and region!='All':
        all_cases = all_cases.filter(region=region)

    historic_cases = all_cases.exclude(case_type='in_intensive_care').exclude(case_type='in_hospital_care')

    ordered_regional_data, regional_data, key_figures = populate_regional_data(historic_cases)

    aggregated = aggregate_by_dates(historic_cases)

    data = {
            'ordered_regional_data': ordered_regional_data,
            'key_figures': key_figures,
            'aggregated': aggregated,
            'all_cases': all_cases
    }

    dump = json.dumps(data, indent=4, sort_keys=False, default=str)

    return HttpResponse(dump, content_type='application/json')

def current_cases(request):
    region = request.GET.get('region', None)
    all_cases = CoronaCase.objects.all().order_by('date')

    if region is not None and region!='All':
        all_cases = all_cases.filter(region=region)

    current_hospital_cases = all_cases.filter(case_type='in_hospital_care') \
                                    .annotate(day=Trunc('date', 'day'))\
                                    .values('day')\
                                    .annotate(cases=Sum('infected'))

    current_intensive_care_cases = all_cases.filter(case_type='in_intensive_care') \
                                    .annotate(day=Trunc('date', 'day'))\
                                    .values('day')\
                                    .annotate(cases=Sum('infected'))

    data = {
        'current_hospital_cases': list(current_hospital_cases),
        'current_intensive_care_cases': list(current_intensive_care_cases)
    }

    dump = json.dumps(data, indent=4, sort_keys=True, default=str)
    return HttpResponse(dump, content_type='application/json')


@xframe_options_exempt
def iframe_test(request):
    template = 'insight/iframe_test.html'

    data, swe_and_avg = load_csv()
    all_cases = CoronaCase.objects.all().order_by('-time_created')[:30]
    cases = CoronaCase.objects.filter(case_type='confirmed')
    ordered_regional_data, regional_data = populate_regional_data(cases)
    total = get_total(cases)
    prognosis = data[10]
    new_cases = get_new_cases(cases)
    total_new = get_total(new_cases)


    death_cases = CoronaCase.objects.filter(case_type='death')
    total_deaths = get_total(death_cases)
    new_death_cases = get_new_cases(death_cases)
    total_new_deaths = get_total(new_death_cases)

    try:
        last_updated = cases.first().time_created
    except:
        last_updated = datetime.now()

    agg_by_dates = aggregate_by_dates(cases)

    return render(request, template, context={
                                            'data': data,
                                            'swe_and_avg': swe_and_avg,
                                            'cases': cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total,
                                            'prognosis': prognosis,
                                            'new_cases': total_new,
                                            'last_updated': last_updated,
                                            'agg_by_dates': agg_by_dates
                                            })
