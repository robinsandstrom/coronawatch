from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data, aggregate_by_dates
from insight.models import Article, CoronaCase, CountryTracker
from datetime import datetime, timedelta
from collections import OrderedDict
from insight.management.commands.new_parser import NewsParser
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum
from insight.SIR import SIR_model
import json
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    date_from = datetime.now()

    template = 'insight/home.html'

    data, swe_and_avg = load_csv()

    all_cases = CoronaCase.objects.all().order_by('-time_created')[:30]
    cases = CoronaCase.objects.filter(case_type='confirmed')
    ordered_regional_data, regional_data = populate_regional_data(cases)
    agg_by_dates = aggregate_by_dates(cases)
    prognosis = data[10]

    total = cases.aggregate(Sum('infected'))['infected__sum'] or 0
    new_cases = cases.filter(date__gte=date_from)
    total_new = new_cases.aggregate(Sum('infected'))['infected__sum'] or 0
    death_cases = CoronaCase.objects.filter(case_type='death')
    total_deaths = death_cases.aggregate(Sum('infected'))['infected__sum'] or 0
    new_death_cases = death_cases.filter(date__gte=date_from)
    total_new_deaths = new_death_cases.aggregate(Sum('infected'))['infected__sum'] or 0

    try:
        last_updated = all_cases.first().time_created
    except:
        last_updated = datetime.now()


    global_ = CountryTracker.objects.filter(country='Global').order_by('date').last()
    norway = CountryTracker.objects.filter(country='Norway').order_by('date').last()
    italy = CountryTracker.objects.filter(country='Italy').order_by('date').last()
    denmark = CountryTracker.objects.filter(country='Denmark').order_by('date').last()

    articles = Article.objects.filter(active=True)

    return render(request, template, context={
                                            'articles': articles,
                                            'data': data,
                                            'swe_and_avg': swe_and_avg,
                                            'cases': all_cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total,
                                            'total_deaths': total_deaths,
                                            'global': global_,
                                            'norway': norway,
                                            'italy': italy,
                                            'denmark': denmark,
                                            'prognosis': prognosis,
                                            'new_cases': total_new,
                                            'total_new_deaths': total_new_deaths,
                                            'last_updated': last_updated,
                                            'agg_by_dates': agg_by_dates
                                            })

def about(request):
    template = 'insight/about.html'
    last_updated = CoronaCase.objects.all().first().time_created
    return render(request, template, context={
                                            'last_updated': last_updated,
                                            })

def modeling(request):
    template = 'insight/modeling.html'
    last_updated = CoronaCase.objects.all().first().time_created
    return render(request, template, context={
                                            'last_updated': last_updated,
                                            })
def update(request):
    template = 'insight/about.html'
    np = NewsParser()
    np.run()
    return HttpResponse('updated')

def get_curve(request):
    alpha = float(request.GET.get('alpha', None) or 0.5)
    gamma = float(request.GET.get('gamma', None) or 1)
    theta = float(request.GET.get('theta', None) or 0.1)
    f = float(request.GET.get('f', None) or 0.97)
    a = float(request.GET.get('a', None) or 0.05)
    P = int(request.GET.get('p_days', None) or 0)
    health_cap = int(request.GET.get('health_cap', None))

    country = request.GET.get('country', None)
    covid19_filename = 'COVID-19-geographic-disbtribution-worldwide-2020-03-14.xls'
    population_filename = 'PopulationByCountry.xlsx'

    sir = SIR_model(covid19_filename, population_filename, country, 500)
    #par = sir.minimize_parameters(f, a) #[alpha_min, theta_min, gamma_min]
    par = [alpha, theta, gamma]
    data, len = sir.get_curve(par, f, a, P)

    dump = json.dumps(data)# + [{'cx':0, 'cy': health_cap},{'cx': len, 'cy':health_cap}])
    return HttpResponse(dump, content_type='application/json')


def get_numbers(request):
    tracked=['Sweden', 'Denmark', 'Norway', 'Spain', 'Germany']
    values = CountryTracker.objects.filter(total_cases__gte=100, country__in=tracked).order_by('date').values('date', 'total_cases','country')
    dump = json.dumps(list(values), indent=4, sort_keys=True, default=str)
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
