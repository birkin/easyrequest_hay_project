# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from . import settings_app
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def info( request ):
    """ Returns basic info. """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    start = datetime.datetime.now()
    context = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=request.scheme, hst=request.META['HTTP_HOST'], uri=request.META.get('REQUEST_URI', request.META['PATH_INFO']) ) },
        'response': {
            'documentation': settings_app.README_URL,
            'elapsed_time': str( datetime.datetime.now() - start ),
            'message': 'ok' } }
    context_json = json.dumps(context, sort_keys=True, indent=2)
    if request.GET.get('format', '') == 'json':
        resp = HttpResponse( context_json, content_type='application/javascript; charset=utf-8' )
    else:
        log.debug( 'context, ```%s```' % pprint.pformat(context) )
        data = { 'context_handle': context_json }
        resp = render( request, 'easyrequest_hay_app_templates/info.html', data )
    return resp


def bul_search( request ):
    """ Triggered by user entering search term into banner.
        Redirects query to search.library.brown.edu """
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    redirect_url = 'https://search.library.brown.edu?%s' % request.META['QUERY_STRING']
    return HttpResponseRedirect( redirect_url )
