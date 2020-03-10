from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data, get_new_cases, get_total, aggregate_by_dates
from insight.models import CoronaCase
from datetime import datetime, timedelta
from collections import OrderedDict

def index(request):
    template = 'insight/home.html'
    data, swe_and_avg = load_csv()
    cases = CoronaCase.objects.all().order_by('-time_created')
    ordered_regional_data, regional_data = populate_regional_data(cases)
    total = get_total(cases)
    prognosis = data[10]
    new_cases = get_new_cases(cases)
    total_new = get_total(new_cases)

    try:
        last_updated = cases.first().time_created+timedelta(hours=1)
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

def about(request):
    template = 'insight/about.html'
    return render(request, template, context={
                                            })
