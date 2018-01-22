# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from easyrequest_hay_app.lib import info_view_helper
from easyrequest_hay_app.lib.aeon import AeonUrlBuilder
from easyrequest_hay_app.lib.session import SessionHelper
from easyrequest_hay_app.lib.time_period_helper import TimePeriodHelper, TimePeriodHandlerHelper
from easyrequest_hay_app.lib.validator import Validator
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)

aeon_url_bldr = AeonUrlBuilder()
sess = SessionHelper()
tm_prd_helper = TimePeriodHelper()
tm_prd_hndler_helper = TimePeriodHandlerHelper()
validator = Validator()


def bul_search( request ):
    """ Triggered by user entering search term into banner-search-field.
        Redirects query to search.library.brown.edu """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    redirect_url = 'https://search.library.brown.edu?%s' % request.META['QUERY_STRING']
    return HttpResponseRedirect( redirect_url )


def info( request ):
    """ Returns basic info. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    start = datetime.datetime.now()
    if request.GET.get('format', '') == 'json':
        context = info_view_helper.build_json_context( start, request.scheme, request.META['HTTP_HOST'], request.META.get('REQUEST_URI', request.META['PATH_INFO'])  )
        context_json = json.dumps(context, sort_keys=True, indent=2)
        resp = HttpResponse( context_json, content_type='application/javascript; charset=utf-8' )
    else:
        context = {}
        resp = render( request, 'easyrequest_hay_app_templates/info.html', context )
    return resp


def time_period( request ):
    """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
        Stores referring url, bib, and item-barcode in session.
        Presents time-period option. """
    log.debug( 'starting time_period view' )
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    if not validator.validate_source(request) and validator.validate_params(request):
        resp = validator.prepare_badrequest_response( request )
    else:
        sess.initialize_session( request )
        shortlink = tm_prd_helper.save_data( json.dumps(request.GET) )
        context = tm_prd_helper.prepare_context( request.GET, shortlink )
        resp = render( request, 'easyrequest_hay_app_templates/time_period.html', context )
    return resp


def time_period_handler( request ):
    """ Handler for time_period `soon=yes/no` selection.
        If `soon=no`, builds Aeon url and redirects.
        Otherwise submits request to millennium, builds Aeon url and redirects. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
    soon_value = request.GET.get( 'soon', '' ).lower()
    if soon_value == 'yes':
        resp = tm_prd_hndler_helper.build_soon_response( request.GET['shortlink'] )
    elif soon_value == 'no':
        aeon_url = aeon_url_bldr.build_aeon_url( item_request.short_url_segment )
        resp = HttpResponseRedirect( aeon_url )
    else:
        resp = HttpResponseRedirect( '%s?message=no time-period information found' % reverse('problem_url') )
    return resp


def login( request ):
    """ Displays millennium shib and non-shib logins.
        Triggered by time_period_hander() """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
    item_callnumber = json.loads(item_request.full_url_params).get( 'item_callnumber', None )
    context = {
        'item_title': item_request.item_title,
        'item_callnumber': item_callnumber,
        'shortlink': request.GET['shortlink'],
        'shib_login_url': reverse('shib_login_url'),
        'barcode_login_url': reverse('barcode_login_url'),
    }
    log.debug( 'context, ```%s```' % pprint.pformat(context) )
    resp = render( request, 'easyrequest_hay_app_templates/login.html', context )
    return resp


def shib_login( request ):
    """ Examines shib headers.
        Redirects user to non-seen processor() view. """
    log.debug( 'starting shib_login()' )
    return HttpResponse( 'shib_login response coming' )
    # ( validity, shib_dict ) = shib_view_helper.check_shib_headers( request )
    # if validity is False:
    #     return_response = shib_view_helper.prep_login_redirect( request )
    # else:
    #     return_response = shib_view_helper.build_response( request, shib_dict )
    # log.debug( 'about to return shib response' )
    # return return_response

def barcode_login( request ):
    """ Examines submitted info.
        Happy path: redirects user to non-seen process() view. """
    log.debug( 'starting barcode_login()' )
    return HttpResponse( 'barcode_login response coming, params perceived, ```<pre>%s</pre>```' % json.dumps(request.POST, sort_keys=True, indent=2) )


def problem( request ):
    return HttpResponse( 'problem handler coming -- message, ```%s```' % request.GET.get('message', 'no_message') )
