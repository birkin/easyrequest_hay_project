import datetime, json, logging, os, pprint, time

from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.utils.http import urlquote as django_urlquote
from easyrequest_hay_app.lib import info_view_helper, version_helper
from easyrequest_hay_app.lib.aeon import AeonUrlBuilder
from easyrequest_hay_app.lib.confirm_helper import ConfirmHelper, ConfirmHandlerHelper
from easyrequest_hay_app.lib.mail import Emailer
from easyrequest_hay_app.lib.millennium import Millennium
from easyrequest_hay_app.lib.session import SessionHelper
from easyrequest_hay_app.lib.shib_helper import ShibViewHelper
from easyrequest_hay_app.lib.sierra import SierraHelper
from easyrequest_hay_app.lib.stats import StatsBuilder
from easyrequest_hay_app.lib.validator import Validator
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)

cnfrm_helper = ConfirmHelper()
emailer = Emailer()
sess = SessionHelper()
shib_view_helper = ShibViewHelper()
stats_builder = StatsBuilder()
validator = Validator()


def confirm( request ):
    """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
        Stores referring url, bib, and item-barcode to db.
        Presents shib and non-shib proceed buttons on confirmation screen. """
    # log.debug( f'request.__dict__, ```{ pprint.pformat(request.__dict__) }```' )
    log.debug( f'request.__dict__, ```{ request.__dict__ }```' )
    if validator.validate_source(request) is False or validator.validate_params(request) is False:
        resp = validator.prepare_badrequest_response( request )
    else:
        sess.initialize_session( request )
        shortlink = cnfrm_helper.save_data( json.dumps(request.GET, sort_keys=True, indent=2) )
        context = cnfrm_helper.prepare_context( request.GET, shortlink )
        resp = cnfrm_helper.prepare_response( request, context )
    log.debug( 'returning resp' )
    return resp


def confirm_handler( request ):
    """ Triggered by confirmation screen's `shib=yes/no` selection.
        If `shib=no`, builds Aeon url and redirects.
        Otherwise redirects to behind-the-scenes `shib_login` url, which will ultimately redirect, behind-the-scenes, to the `processor` url. """
    log.debug( f'request.__dict__, ```{ request.__dict__ }```' )
    cnfrm_hndlr_helper = ConfirmHandlerHelper()
    if validator.validate_source(request) is False or validator.validate_confirm_handler_params(request) is False:
        return validator.prepare_badrequest_response( request )
    type_value = request.GET.get( 'type', '' ).lower()
    cnfrm_hndlr_helper.update_status( type_value, request.GET['shortlink'] )
    if type_value == 'brown shibboleth login':
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.prep_shib_login_stepA(request) )
    elif type_value == 'non-brown login':
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.make_aeon_url(request) )
    else:
        # resp = HttpResponseRedirect( cnfrm_hndlr_helper.get_referring_url(request) )
        resp = HttpResponseRedirect( cnfrm_hndlr_helper.get_referring_url() )
    log.debug( 'returning resp' )
    return resp


def shib_login( request ):
    """ Redirects to shib-SP-login url.
        Specifies the post-login url as the `shib_login_handler` url. """
    time.sleep( .5 )  # in case the IDP logout just-completed needs a breath
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    shortlink = request.GET['shortlink']
    target_url = '%s?shortlink=%s' % ( reverse('shib_login_handler_url'), shortlink )
    log.debug( 'target_url, ```%s```' % target_url )
    if ( request.get_host() == '127.0.0.1' or request.get_host() == '127.0.0.1:8000' ) and project_settings.DEBUG == True:
        redirect_url = target_url
    else:
        redirect_url = '%s?target=%s' % ( settings_app.SHIB_SP_LOGIN_URL, django_urlquote(target_url) )
    log.debug( 'redirect_url, ```%s```' % redirect_url )
    return HttpResponseRedirect( redirect_url )


def shib_login_handler( request ):
    """ Behind-the-scenes, examines shib headers.
        Redirects user to behind-the-scenes processor() view. """
    log.debug( 'starting shib_login_handler(); request.__dict__, ```%s```' % request.__dict__ )
    ( validity, shib_dict ) = shib_view_helper.check_shib_headers( request )
    if validity is False:  # TODO: implement this
        resp = shib_view_helper.prep_login_redirect( request )
    else:
        resp = shib_view_helper.build_processor_response( request.GET['shortlink'], shib_dict )
    log.debug( 'about to return shib response' )
    return resp


def processor( request ):
    """ Behind-the-scenes url which handles item request...
        - Gets item-id.
        - Attempts to place hold in Sierra.
        - Redirects user to Aeon.
        Triggered after a successful shib_login (along with patron-api lookup) """
    log.debug( f'starting processor(); request.__dict__, ```{request.__dict__}```' )
    sierra_hlpr = SierraHelper()
    aeon_url_bldr = AeonUrlBuilder()
    shortlink = request.GET['shortlink']
    log.debug( 'shortlink, `%s`' % shortlink )
    sierra_hlpr.prep_item_data( shortlink )  # performs db lookup and contains instantiated orm object
    if sierra_hlpr.item_id:  # if we couldn't get an item-id, we can't place a hold
        sierra_hlpr.manage_place_hold()
    if sierra_hlpr.send_email_check() is True:
        item_json = json.dumps(sierra_hlpr.item_dct, sort_keys=True, indent=2)
        emailer.send_staff_problem_email( sierra_hlpr.item_request.patron_info, item_json )
    aeon_url_bldr.make_millennium_note( sierra_hlpr.item_id, sierra_hlpr.item_barcode, sierra_hlpr.patron_barcode, sierra_hlpr.hold_status )
    # aeon_url = aeon_url_bldr.build_aeon_url( shortlink )
    aeon_url = aeon_url_bldr.build_aeon_url( sierra_hlpr.item_dct )
    return HttpResponseRedirect( aeon_url )


# def processor( request ):
#     """ Behind-the-scenes url which handles item request...
#         - Gets item-id.
#         - Attempts to place hold in Sierra.
#         - Redirects user to Aeon.
#         Triggered after a successful shib_login (along with patron-api lookup) """
#     log.debug( 'starting processor(); request.__dict__, ```%s```' % request.__dict__ )
#     mill_hlpr = Millennium()
#     aeon_url_bldr = AeonUrlBuilder()
#     shortlink = request.GET['shortlink']
#     log.debug( 'shortlink, `%s`' % shortlink )
#     mill_hlpr.prep_item_data( shortlink )
#     if mill_hlpr.item_id:  # if we couldn't get an item-id, we can't place a hold
#         mill_hlpr.call_place_hold()
#     emailer.run_send_check( mill_hlpr.item_id, mill_hlpr.hold_status, shortlink )
#     aeon_url_bldr.make_millennium_note( mill_hlpr.item_id, mill_hlpr.item_barcode, mill_hlpr.patron_barcode, mill_hlpr.hold_status )
#     aeon_url = aeon_url_bldr.build_aeon_url( shortlink )
#     return HttpResponseRedirect( aeon_url )


def problem( request ):
    """ Displays to user a problem message.
        Could be used by a variety of failure situations.
        Currently used by failure of shib-authentication. """
    resp = render( request, 'easyrequest_hay_app_templates/problem.html', {} )
    return resp


def stats( request ):
    """ Prepares stats for given dates; returns json. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    ## grab & validate params
    if stats_builder.check_params( request.GET, request.scheme, request.META['HTTP_HOST'] ) == False:
        return HttpResponseBadRequest( stats_builder.output, content_type=u'application/javascript; charset=utf-8' )
    ## query records for period (parse them via source)
    requests = stats_builder.run_query()
    ## process results
    data = stats_builder.process_results( requests )
    ## build response
    stats_builder.build_response( data, request.scheme, request.META['HTTP_HOST'], request.GET )
    return HttpResponse( stats_builder.output, content_type=u'application/javascript; charset=utf-8' )


# ===========================
# helpers
# ===========================


def bul_search( request ):
    """ Triggered by user entering search term into banner-search-field.
        Redirects query to search.library.brown.edu """
    log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
    redirect_url = 'https://search.library.brown.edu?%s' % request.META['QUERY_STRING']
    return HttpResponseRedirect( redirect_url )


def info( request ):
    """ Returns basic info about the easyrequest_hay webapp.
        Triggered by root easyrequest_hay url. """
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



# ===========================
# for development convenience
# ===========================


def version( request ):
    """ Returns basic branch and commit data. """
    rq_now = datetime.datetime.now()
    commit = version_helper.get_commit()
    branch = version_helper.get_branch()
    info_txt = commit.replace( 'commit', branch )
    context = version_helper.make_context( request, rq_now, info_txt )
    output = json.dumps( context, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def error_check( request ):
    """ For checking that admins receive error-emails. """
    if project_settings.DEBUG == True:
        1/0
    else:
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )
