# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from easyrequest_hay_app.lib import info_view_helper
from easyrequest_hay_app.lib.session import SessionHelper
from easyrequest_hay_app.lib.time_period_helper import TimePeriodHelper
from easyrequest_hay_app.lib.validator import Validator
# from easyrequest_hay_app.lib.login_view_helper import LoginViewHelper


log = logging.getLogger(__name__)
sess = SessionHelper()
tm_prd_helper = TimePeriodHelper()
validator = Validator()
# lg_vw_helper = LoginViewHelper()


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
    if not validator.validate_source(request) and validator.validate_params(request):
        resp = validator.prepare_badrequest_response( request )
    else:
        sess.initialize_session( request )
        sess.update_session( request, key='item_title', val=request.GET['item_title'] )
        context = tm_prd_helper.prepare_context( request.session )
        resp = render( request, 'easyrequest_hay_app_templates/time_period.html', context )
    return resp


def time_period_handler( request ):
    return HttpResponse( 'coming' )


# def login( request ):
#     """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
#         Stores referring url, bib, and item-barcode in session.
#         Presents shib and manual log in options. """
#     log.debug( 'starting login view' )  # log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
#     if not ( lg_vw_helper.validate_source(request) and lg_vw_helper.validate_params(request) ):
#         resp = lg_vw_helper.prepare_badrequest_response( request )
#     else:
#         lg_vw_helper.initialize_session( request )
#         ( title, callnumber, item_id ) = lg_vw_helper.get_item_info( request.GET['bibnum'], request.GET['barcode'] )
#         lg_vw_helper.update_session( request, title, callnumber, item_id )
#         context = lg_vw_helper.prepare_context( request )
#         resp = render( request, 'easyrequest_hay_app_templates/login.html', context )
#     return resp
