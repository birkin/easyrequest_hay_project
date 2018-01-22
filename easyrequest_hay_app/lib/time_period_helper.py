# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, urllib
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.template import loader
from django.core.urlresolvers import reverse
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class TimePeriodHelper( object ):
    """ Contains helpers for views.time_period() for handling GET. """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def save_data( self, jsonified_querydct ):
        """ Saves data.
            Called by views.time_period() """
        log.debug( 'jsonified_querydct, ```%s```' % jsonified_querydct )
        dct = json.loads( jsonified_querydct )
        log.debug( 'dct, ```%s```' % pprint.pformat(dct) )
        itmrqst = ItemRequest()
        itmrqst.item_title = dct['item_title']
        itmrqst.full_url_params = jsonified_querydct
        itmrqst.short_url_segment = self.epoch_micro_to_str()
        itmrqst.save()
        return itmrqst.short_url_segment

    def prepare_context( self, original_params, shortlink_segment ):
        """ Prepares vars for template.
            Called by views.time_period() """
        item_request = ItemRequest.objects.get( short_url_segment=shortlink_segment )
        item_callnumber = json.loads(item_request.full_url_params).get( 'item_callnumber', None )
        context = {
            'item_title': original_params['item_title'],
            'item_callnumber': item_callnumber,
            'action_url': reverse( 'time_period_handler_url' ),
            'shortlink_segment': shortlink_segment
        }
        log.debug( 'context, ```%s```' % pprint.pformat(context) )
        return context

    def epoch_micro_to_str( self, n=None, base=None ):
        """ Returns string for shortlink based on the number of microseconds since the epoch.
            Not currently called.
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

    ## end class TimePeriodHelper


class TimePeriodHandlerHelper( object ):
    """ Contains helpers for views.time_period_handler(). """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def build_soon_response( self, shortlink ):
        """ Builds redirect response to login for millennium submission. """
        redirect_url = '%s?shortlink_segment=%s' % ( reverse('login_url'), shortlink )
        log.debug( 'redirect_url, ```%s```' % redirect_url )
        resp = HttpResponseRedirect( redirect_url )
        return resp

    ## end class TimePeriodHandlerHelper
