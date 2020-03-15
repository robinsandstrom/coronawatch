from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data, aggregate_by_dates
from insight.models import Article, CoronaCase, CountryTracker
from datetime import datetime, timedelta
from collections import OrderedDict
from insight.management.commands.new_parser import NewsParser
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum
import json

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
    alpha = request.GET.get('alpha', None)
    gamma = request.GET.get('gamma', None)
    theta = request.GET.get('theta', None)

    data = [{
      "ax": 1,
      "ay": 0.5,
      "bx": 1,
      "by": 20
    }, {
      "ax": 2,
      "ay": 1.3,
      "bx": 2,
      "by": 4.9
    }, {
      "ax": 3,
      "ay": 2.3,
      "bx": 3,
      "by": 5.1
    }, {
      "ax": 4,
      "ay": 2.8,
      "bx": 4,
      "by": 5.3
    }, {
      "ax": 5,
      "ay": 3.5,
      "bx": 5,
      "by": 6.1
    }, {
      "ax": 6,
      "ay": 5.1,
      "bx": 6,
      "by": 8.3
    }, {
      "ax": 7,
      "ay": 6.7,
      "bx": 7,
      "by": 10.5
    }, {
      "ax": 8,
      "ay": 8,
      "bx": 8,
      "by": 12.3
    }, {
      "ax": 9,
      "ay": 8.9,
      "bx": 9,
      "by": 14.5
    }, {
      "ax": 10,
      "ay": 9.7,
      "bx": 10,
      "by": 15
    }, {
      "ax": 11,
      "ay": 10.4,
      "bx": 11,
      "by": 18.8
    }, {
      "ax": 12,
      "ay": 11.7,
      "bx": 12,
      "by": 19
    }]
    dump = json.dumps(data)
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
