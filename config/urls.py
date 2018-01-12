# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from easyrequest_hay_app import views


admin.autodiscover()


urlpatterns = [

    url( r'^admin/', admin.site.urls ),  # eg host/project_x/admin/

    url( r'^info/$', views.info, name='info_url' ),

    url( r'^bul_search/$', views.bul_search, name='bul_search_url' ),

    url( r'^time_period/$', views.time_period, name='time_period_url' ),

    # url( r'^login/$', views.login, name='login_url' ),

    url( r'^$', RedirectView.as_view(pattern_name='info_url') ),

    ]
