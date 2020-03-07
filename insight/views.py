from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data
from insight.models import CoronaCase
from datetime import datetime

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

    return render(request, template, context={
                                            'data': data,
                                            'cases': cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total,
                                            'prognosis': prognosis
                                            })
