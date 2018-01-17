# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, urllib
from django.http import HttpResponseBadRequest
from django.template import loader
from django.core.urlresolvers import reverse
# from easyrequest_hay_app.lib.pickup_location import PickupLocation
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)
# pick_location = PickupLocation()


class TimePeriodHelper( object ):
    """ Contains helpers for views.request_def() for handling GET. """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def save_data( self, request_path, jsonified_querydct ):
        """ Saves data.
            Called by views.time_period() """
        log.debug( 'type(request_path, `%s`' % type(request_path) )
        log.debug( 'jsonified_querydct, ```%s```' % jsonified_querydct )

        itmrqst = ItemRequest()
        itmrqst.full_url_params = jsonified_querydct
        itmrqst.short_url_segment = self.epoch_micro_to_str()
        itmrqst.save()
        return

    def prepare_context( self, original_params ):
        """ Prepares vars for template.
            Called by views.time_period() """
        # log.debug( 'type(original_params), `%s`' % type(original_params) )
        # log.debug( 'original_params, ```%s```' % pprint.pformat(original_params) )
        context = {
            'item_title': original_params['item_title'],
            'action_url': reverse( 'time_period_handler_url' ),
            'original_params_json': json.dumps(original_params) # urllib.parse.quote( original_params )
        }
        log.debug( 'context, ```%s```' % context )
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

    # end class TimePeriodHelper


