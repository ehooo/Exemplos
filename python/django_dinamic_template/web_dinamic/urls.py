from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

def dinamic_url(request, path):
    return render_to_response(path+'.html', { }, RequestContext(request))


urlpatterns = patterns(
    '',
    url(r'^(?P<path>[\w\ -_/]+)$', dinamic_url, name='dinamic_url'),
)
