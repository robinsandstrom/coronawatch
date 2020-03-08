from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data
from insight.models import CoronaCase
from datetime import datetime, timedelta

def index(request):
    template = 'insight/home.html'
    data = load_csv()
    cases = CoronaCase.objects.all().order_by('-date')
    ordered_regional_data, regional_data = populate_regional_data(cases)

    total = 0

    for case in cases:
        total+=case.infected

    date = datetime.today()
    prognosis = data[8]

    date_from = datetime.now() - timedelta(days=1)

    new_cases = cases.filter(date__gte=date_from)

    total_new = 0
    for case in new_cases:
        total_new+=case.infected

    last_updated = cases.last().date

    return render(request, template, context={
                                            'data': data,
                                            'cases': cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total,
                                            'prognosis': prognosis,
                                            'new_cases': total_new,
                                            'last_updated': last_updated
                                            })
