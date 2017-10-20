from django.shortcuts import render

# Create your views here.

def topology(request):
    return render (request, 'topology.html')

def topology_3(request):
    return render (request, '3.html')

def topology_5(request):
    return render (request, '5.html')

def topology_6(request):
    return render (request, '6.html')

def topology_7(request):
    return render (request, '7.html')

def topology_8(request):
    return render (request, '8.html')

