from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv
from insight.models import CoronaCase

def index(request):
    template = 'insight/home.html'
    data = load_csv()
    cases = CoronaCase.objects.all().order_by('date')
    return render(request, template, context={
                                            'data': data,
                                            'cases': cases
                                            })
