# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def info( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now time, `%s`' % now )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )
