# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from easyrequest_hay_app import views


admin.autodiscover()


urlpatterns = [

    url( r'^admin/', admin.site.urls ),  # eg host/project_x/admin/

    url( r'^bul_search/$', views.bul_search, name='bul_search_url' ),

    url( r'^info/$', views.info, name='info_url' ),

    url( r'^confirm/$', views.confirm, name='confirm_url' ),

    url( r'^confirm_handler/$', views.confirm_handler, name='confirm_handler_url' ),

    # url( r'^time_period/$', views.time_period, name='time_period_url' ),

    # url( r'^time_period_handler/$', views.time_period_handler, name='time_period_handler_url' ),

    url( r'^problem/$', views.problem, name='problem_url' ),

    # url( r'^login/$', views.login, name='login_url' ),

    url( r'^shib_login/$', views.shib_login, name='shib_login_url' ),

    # url( r'^barcode_login/$', views.barcode_login, name='barcode_login_url' ),

    url( r'^processor/$', views.processor, name='processor_url' ),

    url( r'^$', RedirectView.as_view(pattern_name='info_url') ),

    ]
