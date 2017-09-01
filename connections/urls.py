from django.shortcuts import render
from django.http import HttpResponse
from . import views

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'connections_real_time', views.connections_real),
    url(r'connections_last_time', views.connections_last),
    url(r'', views.connections),
]
