# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from easyrequest_hay_app.lib import info_view_helper
from easyrequest_hay_app.lib.login_view_helper import LoginViewHelper


log = logging.getLogger(__name__)
lv_helper = LoginViewHelper()


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


def bul_search( request ):
    """ Triggered by user entering search term into banner-search-field.
        Redirects query to search.library.brown.edu """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    redirect_url = 'https://search.library.brown.edu?%s' % request.META['QUERY_STRING']
    return HttpResponseRedirect( redirect_url )


def login( request ):
    """ Triggered by user clicking on an Annex-Hay Josiah `request-access` link.
        Stores referring url, bib, and item-barcode in session.
        Presents shib and manual log in options. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    if not ( lv_helper.validate_source(request) and lv_helper.validate_params(request) ):
        # return HttpResponseBadRequest( "This web-application supports Josiah, the Library's search web-application. If you think you should be able to access this url, please contact '%s'." % lv_helper.EMAIL_AUTH_HELP )
        template = loader.get_template('easyrequest_hay_app_templates/problem.html')
        context = {
            'help_email': lv_helper.EMAIL_AUTH_HELP,
        }
        return HttpResponseBadRequest( template.render(context, request) )


        resp = HttpResponseBadRequest( context_json, content_type='application/javascript; charset=utf-8' )
    lv_helper.initialize_session( request )
    ( title, callnumber, item_id ) = lv_helper.get_item_info( request.GET['bibnum'], request.GET['barcode'] )
    lv_helper.update_session( request, title, callnumber, item_id )
    context = lv_helper.prepare_context( request )
    return render( request, 'easyrequest_hay_app_templates/login.html', context )
