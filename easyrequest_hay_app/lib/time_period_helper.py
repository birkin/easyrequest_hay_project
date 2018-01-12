# -*- coding: utf-8 -*-

import json, logging, os, pprint, urllib
from django.http import HttpResponseBadRequest
from django.template import loader
from easyrequest_hay_app.lib.pickup_location import PickupLocation


log = logging.getLogger(__name__)
pick_location = PickupLocation()


class TimePeriodHelper( object ):
    """ Contains helpers for views.request_def() for handling GET. """

    def __init__( self ):
        """ Holds env-vars. """
        pass

    def prepare_context( self ):
        """ Prepares vars for template.
            Called by views.login() """
        context = {}
        return context

    # end class TimePeriodHelper
