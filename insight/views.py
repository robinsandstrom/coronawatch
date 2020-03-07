from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv, populate_regional_data
from insight.models import CoronaCase

def index(request):
    template = 'insight/home.html'
    data = load_csv()
    cases = CoronaCase.objects.all().order_by('date')
    ordered_regional_data, regional_data = populate_regional_data(cases)

    total = 0

    for case in cases:
        total+=case.infected


    return render(request, template, context={
                                            'data': data,
                                            'cases': cases,
                                            'regional_data': regional_data,
                                            'ordered_regional_data': ordered_regional_data,
                                            'total': total
                                            })
