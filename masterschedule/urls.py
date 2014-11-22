from django.shortcuts import redirect
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/profile/$', lambda *args: redirect("conferences")),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'', include('schedule.urls')),
)
