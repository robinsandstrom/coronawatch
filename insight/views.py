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


def index(request):
    date_from = datetime.now()

    template = 'insight/home.html'

    data, swe_and_avg = load_csv()

    all_cases = CoronaCase.objects.all().order_by('-time_created')
    ordered_regional_data, regional_data = populate_regional_data(all_cases)

    aggregated = aggregate_by_dates(all_cases)

    cases = all_cases.filter(case_type='confirmed')
    total = cases.aggregate(Sum('infected'))['infected__sum'] or 0
    new_cases = cases.filter(case_type='confirmed', date__gte=date_from)
    total_new = new_cases.aggregate(Sum('infected'))['infected__sum'] or 0

    death_cases = CoronaCase.objects.filter(case_type='death')
    total_deaths = death_cases.aggregate(Sum('infected'))['infected__sum'] or 0
    new_death_cases = death_cases.filter(date__gte=date_from)
    total_new_deaths = new_death_cases.aggregate(Sum('infected'))['infected__sum'] or 0

    intensive_care_cases = all_cases.filter(case_type='intensive_care')
    total_ivs = intensive_care_cases.aggregate(Sum('infected'))['infected__sum'] or 0
    new_iv_cases = intensive_care_cases.filter(date__gte=date_from)
    total_new_ivs = new_iv_cases.aggregate(Sum('infected'))['infected__sum'] or 0

    try:
        last_updated = all_cases.first().time_created
    except:
        last_updated = datetime.now()

    articles = Article.objects.all().order_by('-time_created')[0:10]

    return render(request, template, context={
                                            'articles': articles,
                                            'data': data,
                                            'cases': all_cases.filter(text__isnull=False)[0:30],
                                            'intensive_care_cases': intensive_care_cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total,
                                            'total_deaths': total_deaths,
                                            'total_ivs': total_ivs,
                                            'total_new_ivs': total_new_ivs,
                                            'new_cases': total_new,
                                            'total_new_deaths': total_new_deaths,
                                            'last_updated': last_updated,
                                            'aggregated': aggregated,
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
    return
    tracked=['Sweden', 'Denmark', 'Norway', 'Spain', 'Germany']
    values = CountryTracker.objects.filter(total_cases__gte=100, country__in=tracked).order_by('date').values('date', 'total_cases','country')


    dump = json.dumps(list(values), indent=4, sort_keys=True, default=str)
    print(dump)
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
