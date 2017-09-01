from django.shortcuts import render

# Create your views here.

def topology(request):
    return render (request, 'topology.html')