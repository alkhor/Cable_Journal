from django.shortcuts import render
from django.http import HttpResponse
from . import views

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^3', views.topology_3),
    url(r'^5', views.topology_5),
    url(r'^6', views.topology_6),
    url(r'^7', views.topology_7),
    url(r'^8', views.topology_8),
    url(r'', views.topology),
]
