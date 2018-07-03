# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, urllib
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from easyrequest_hay_app.lib.aeon import AeonUrlBuilder
from easyrequest_hay_app.lib.shib_helper import ShibLoginHelper
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)
shib_login_helper = ShibLoginHelper()


class ConfirmHelper( object ):
    """ Contains helpers for views.confirm() for handling GET. """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def save_data( self, jsonified_querydct ):
        """ Saves data.
            Called by views.confirm() """
        log.debug( 'jsonified_querydct, ```%s```' % jsonified_querydct )
        dct = json.loads( jsonified_querydct )
        log.debug( 'dct, ```%s```' % pprint.pformat(dct) )
        itmrqst = ItemRequest()
        itmrqst.item_title = dct['item_title']
        itmrqst.full_url_params = jsonified_querydct
        itmrqst.short_url_segment = self.epoch_micro_to_str()
        itmrqst.status = 'initial_landing'
        itmrqst.save()
        return itmrqst.short_url_segment

    def prepare_context( self, original_params, shortlink ):
        """ Prepares vars for template.
            Called by views.confirm() """
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        item_callnumber = json.loads(item_request.full_url_params).get( 'item_callnumber', None )
        context = {
            'item_title': original_params['item_title'],
            'item_callnumber': item_callnumber,
            'action_url': reverse( 'confirm_handler_url' ),
            'shortlink': shortlink,
        }
        log.debug( 'context, ```%s```' % pprint.pformat(context) )
        return context

    def epoch_micro_to_str( self, n=None, base=None ):
        """ Returns string for shortlink based on the number of microseconds since the epoch.
            Called by save_data()
            Based on code from <http://interactivepython.org/runestone/static/pythonds/Recursion/pythondsConvertinganIntegertoaStringinAnyBase.html> """
        if n is None:
            epoch_datetime = datetime.datetime( 1970, 1, 1, tzinfo=datetime.timezone.utc )
            n = epoch_microseconds = int( (datetime.datetime.now(tz=datetime.timezone.utc) - epoch_datetime).total_seconds() * 1000000 )
        convert_string = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789"
        if base is None:
            base = len( convert_string )
        if n < base:
            return convert_string[n]
        else:
            return self.epoch_micro_to_str( n//base, base ) + convert_string[n%base]  # the `//` is a math.floor() function

    def prepare_response( self, request, context ):
        """ Prepares json or html response.
            Called by views.confirm() """
        if request.GET.get('output', '') == 'json':
            output = json.dumps( context, sort_keys=True, indent=2 )
            resp = HttpResponse( output, content_type=u'application/javascript; charset=utf-8' )
        else:
            resp = render( request, 'easyrequest_hay_app_templates/confirm.html', context )
        log.debug( 'type(resp), `%s`' % type(resp) )
        return resp


    ## end class TimePeriodHelper


class ConfirmHandlerHelper( object ):
    """ Contains helpers for views.confirm_handler(). """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def update_status( self, handle_type, shortlink ):
        """ Updates status, primarily for stats-tracking.
            Called by views.confirm_handler() """
        itmrqst = ItemRequest.objects.get( short_url_segment=shortlink )
        if handle_type == 'brown shibboleth login':
            status = 'to_aeon_via_shib'
        elif handle_type == 'non-brown login':
            status = 'to_aeon_directly'
        else:
            status = 'back_to_josiah'
        itmrqst.status = status
        itmrqst.save()
        log.debug( 'status updated to, `%s`' % itmrqst.status )
        return

    def prep_shib_login_stepA( self, request ):
        """ Prepares shib-login url.
            Called by views.confirm_handler() """
        login_a_url = shib_login_helper.prep_login_url_stepA( request )
        return login_a_url

    def make_aeon_url( self, request ):
        """ Prepares aeon url.
            Called by views.confirm_handler() """
        aeon_url_bldr = AeonUrlBuilder()
        shortlink = request.GET['shortlink']
        aeon_url = aeon_url_bldr.build_aeon_url( shortlink )
        log.debug( 'aeon_url, ```%s```' % aeon_url )
        return aeon_url

    def get_referring_url( self, request ):
        """ Returns referring url.
            Called by views.confirm_handler() """
        shortlink = request.GET['shortlink']
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        item_dct = json.loads( item_request.full_url_params )
        referring_url = item_dct['referring_url']
        log.debug( 'referring_url ```%s```' % referring_url )
        return referring_url

    ## end class TimePeriodHandlerHelper
