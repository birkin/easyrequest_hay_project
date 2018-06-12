# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.http import urlquote as django_urlquote
from easyrequest_hay_app.lib import info_view_helper, login_view_helper
from easyrequest_hay_app.lib.aeon import AeonUrlBuilder
from easyrequest_hay_app.lib.confirm_helper import ConfirmHelper, ConfirmHandlerHelper
from easyrequest_hay_app.lib.millennium import Millennium
from easyrequest_hay_app.lib.session import SessionHelper
from easyrequest_hay_app.lib.shib_helper import ShibViewHelper
from easyrequest_hay_app.lib.time_period_helper import TimePeriodHelper, TimePeriodHandlerHelper
from easyrequest_hay_app.lib.validator import Validator
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)

cnfrm_helper = ConfirmHelper()
cnfrm_hndlr_helper = ConfirmHandlerHelper()
millennium = Millennium()
sess = SessionHelper()
shib_view_helper = ShibViewHelper()
tm_prd_helper = TimePeriodHelper()
tm_prd_hndler_helper = TimePeriodHandlerHelper()
validator = Validator()


def bul_search( request ):
    """ Triggered by user entering search term into banner-search-field.
        Redirects query to search.library.brown.edu """
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    redirect_url = 'https://search.library.brown.edu?%s' % request.META['QUERY_STRING']
    return HttpResponseRedirect( redirect_url )


def info( request ):
    """ Returns basic info. """
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    start = datetime.datetime.now()
    if request.GET.get('format', '') == 'json':
        context = info_view_helper.build_json_context( start, request.scheme, request.META['HTTP_HOST'], request.META.get('REQUEST_URI', request.META['PATH_INFO'])  )
        context_json = json.dumps(context, sort_keys=True, indent=2)
        resp = HttpResponse( context_json, content_type='application/javascript; charset=utf-8' )
    else:
        context = {}
        resp = render( request, 'easyrequest_hay_app_templates/info.html', context )
    return resp


def confirm( request ):
    """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
        Stores referring url, bib, and item-barcode in session.
        Presents shib and non-shib proceed buttons. """
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    if not validator.validate_source(request) and validator.validate_params(request):
        resp = validator.prepare_badrequest_response( request )
    else:
        sess.initialize_session( request )
        shortlink = cnfrm_helper.save_data( json.dumps(request.GET, sort_keys=True, indent=2) )
        context = cnfrm_helper.prepare_context( request.GET, shortlink )
        resp = cnfrm_helper.prepare_response( request, context )
    return resp

def confirm_handler( request ):
    """ Handler for confirm `shib=yes/no` selection.
        If `shib=no`, builds Aeon url and redirects.
        Otherwise submits request to millennium, builds Aeon url and redirects. """
    type_value = request.GET.get( 'type', '' ).lower()
    log.debug( 'type_value, `%s`' % type_value )
    if type_value == 'brown shibboleth login':
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.prep_shib_login_stepA(request) )
    elif type_value == 'non-brown login':
        # message = '<p>not-yet-implemented &mdash; this will land the user at Aeon (_not_ having placed the annex-request in millennium).</p>'
        # resp = HttpResponse( message )
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.make_aeon_url(request) )
    else:
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.get_referring_url(request) )
    return resp

def shib_login( request ):
    """ Redirects to shib-SP-login url. """
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    shortlink = request.GET['shortlink']
    target_url = '%s://%s%s?shortlink=%s' % ( request.scheme, request.get_host(), reverse('shib_login_handler_url'), shortlink )
    log.debug( 'target_url, ```%s```' % target_url )
    sp_login_url = '%s?target=%s' % ( settings_app.SHIB_SP_LOGIN_URL, django_urlquote(target_url) )
    log.debug( 'sp_login_url, ```%s```' % sp_login_url )
    return HttpResponseRedirect( sp_login_url )

# def shib_login( request ):
#     """ Examines shib headers.
#         Redirects user to non-seen processor() view. """
#     log.debug( 'starting shib_login(); request.__dict__, ```%s```' % request.__dict__ )
#     ( validity, shib_dict ) = shib_view_helper.check_shib_headers( request )
#     if validity is False:  # TODO: implement this
#         resp = shib_view_helper.prep_login_redirect( request )
#     else:
#         resp = shib_view_helper.build_processor_response( request.GET['shortlink'], shib_dict )
#     log.debug( 'about to return shib response' )
#     return resp

def shib_login_handler( request ):
    """ Examines shib headers.
        Redirects user to non-seen processor() view. """
    log.debug( 'starting shib_login(); request.__dict__, ```%s```' % request.__dict__ )
    ( validity, shib_dict ) = shib_view_helper.check_shib_headers( request )
    if validity is False:  # TODO: implement this
        resp = shib_view_helper.prep_login_redirect( request )
    else:
        resp = shib_view_helper.build_processor_response( request.GET['shortlink'], shib_dict )
    log.debug( 'about to return shib response' )
    return resp

def processor( request ):
    """ Handles item request:,
        - Ensures user is authenticated.
        - Gets item-id.
        - Places hold.
        - Emails patron.
        - Triggers shib_logout() view.
        Triggered after a successful shib_login (along with patron-api lookup) """
    log.debug( 'starting processor(); request.__dict__, ```%s```' % request.__dict__ )
    aeon_url_bldr = AeonUrlBuilder()
    shortlink = request.GET['shortlink']
    log.debug( 'shortlink, `%s`' % shortlink )
    item_id = millennium.get_item_id( shortlink )
    1/0
    # err = millennium.place_hold( item_id )
    # err = emailer.send_email( shortlink )
    aeon_url_bldr.make_millennium_note( item_id )
    aeon_url = aeon_url_bldr.build_aeon_url( shortlink )
    return HttpResponseRedirect( aeon_url )

def problem( request ):
    return HttpResponse( 'problem handler coming -- message, ```%s```' % request.GET.get('message', 'no_message') )


    # log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    # aeon_url_bldr = AeonUrlBuilder()
    # item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
    # soon_value = request.GET.get( 'soon', '' ).lower()
    # if soon_value == 'yes':
    #     resp = tm_prd_hndler_helper.build_soon_response( request.GET['shortlink'] )
    # elif soon_value == 'no':
    #     resp = HttpResponseRedirect( aeon_url_bldr.build_aeon_url(item_request.short_url_segment) )
    # else:
    #     resp = HttpResponseRedirect( '%s?message=no time-period information found' % reverse('problem_url') )
    # return resp


# def confirm_handler( request ):
#     """ Handler for confirm `shib=yes/no` selection.
#         If `shib=no`, builds Aeon url and redirects.
#         Otherwise submits request to millennium, builds Aeon url and redirects. """
#     type_value = request.GET.get( 'type', '' ).lower()
#     log.debug( 'type_value, `%s`' % type_value )
#     if type_value == 'brown shibboleth login':
#         message = '<p>not-yet-implemented &mdash; this will display the shib login, then land at Aeon (and behind-the-scenes _will_ have placed the annex-request in millennium).</p>'
#     elif type_value == 'non-brown login':
#         message = '<p>not-yet-implemented &mdash; this will land the user at Aeon (_not_ having placed the annex-request in millennium).</p>'
#     else:
#         message = '<p>not-yet-implemented &mdash; this will the patron to the page from whence she came.</p>'
#     return HttpResponse( message )
#     # log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
#     # aeon_url_bldr = AeonUrlBuilder()
#     # item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
#     # soon_value = request.GET.get( 'soon', '' ).lower()
#     # if soon_value == 'yes':
#     #     resp = tm_prd_hndler_helper.build_soon_response( request.GET['shortlink'] )
#     # elif soon_value == 'no':
#     #     resp = HttpResponseRedirect( aeon_url_bldr.build_aeon_url(item_request.short_url_segment) )
#     # else:
#     #     resp = HttpResponseRedirect( '%s?message=no time-period information found' % reverse('problem_url') )
#     # return resp


# def time_period( request ):
#     """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
#         Stores referring url, bib, and item-barcode in session.
#         Presents time-period option. """
#     log.debug( 'starting time_period view' )
#     log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
#     if not validator.validate_source(request) and validator.validate_params(request):
#         resp = validator.prepare_badrequest_response( request )
#     else:
#         sess.initialize_session( request )
#         shortlink = tm_prd_helper.save_data( json.dumps(request.GET, sort_keys=True, indent=2) )
#         context = tm_prd_helper.prepare_context( request.GET, shortlink )
#         resp = render( request, 'easyrequest_hay_app_templates/time_period.html', context )
#     return resp


# def time_period_handler( request ):
#     """ Handler for time_period `soon=yes/no` selection.
#         If `soon=no`, builds Aeon url and redirects.
#         Otherwise submits request to millennium, builds Aeon url and redirects. """
#     log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
#     aeon_url_bldr = AeonUrlBuilder()
#     item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
#     soon_value = request.GET.get( 'soon', '' ).lower()
#     if soon_value == 'yes':
#         resp = tm_prd_hndler_helper.build_soon_response( request.GET['shortlink'] )
#     elif soon_value == 'no':
#         resp = HttpResponseRedirect( aeon_url_bldr.build_aeon_url(item_request.short_url_segment) )
#     else:
#         resp = HttpResponseRedirect( '%s?message=no time-period information found' % reverse('problem_url') )
#     return resp


# def login( request ):
#     """ Displays millennium shib and non-shib logins.
#         Triggered by time_period_hander() """
#     log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
#     item_request = get_object_or_404( ItemRequest, short_url_segment=request.GET.get('shortlink', 'foo') )
#     item_callnumber = json.loads(item_request.full_url_params).get( 'item_callnumber', None )
#     context = login_view_helper.build_login_context( item_request, request.GET['shortlink'], item_callnumber )
#     log.debug( 'context, ```%s```' % pprint.pformat(context) )
#     resp = render( request, 'easyrequest_hay_app_templates/login.html', context )
#     return resp


# def barcode_login( request ):
#     """ Examines submitted info.
#         Happy path: redirects user to non-seen process() view. """
#     log.debug( 'starting barcode_login(); request.__dict__, ```%s```' % request.__dict__ )
#     return HttpResponse( 'barcode_login response coming, params perceived, ```<pre>%s</pre>```' % json.dumps(request.POST, sort_keys=True, indent=2) )
