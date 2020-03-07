from django.http import HttpResponse
from django.shortcuts import render

from insight.backend import load_csv

def index(request):
    template = 'insight/home.html'
    data = load_csv()
    return render(request, template, context={
                                            'data': data,
                                            })
