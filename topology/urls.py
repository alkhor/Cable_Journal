from django.shortcuts import render
from django.http import HttpResponse
from . import views

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'', views.topology),
]
