# -*- coding: utf-8 -*-

import datetime, logging
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class ExpirationManager( object ):
    """ Validates source and params for incoming `time_period` request. """

    def __init__( self, days=None ):
        pass

    def clean_patron_data( self ):
        """ Grabs older files and ensures identifying data has been removed.
            Called by cron-script. """
        log.debug( 'starting clean' )
        filter_datetime = self.calculate_filter_datetime()
        requests = ItemRequest.objects.filter( create_datetime__lte=filter_datetime )
        for request in requests:
            self.clean_request( request )
        log.debug( '`%s` requests cleaned' % len(requests) )
        return

    def calculate_filter_datetime( self ):
        """ Returns past date.
            Called by clean_patron_data() """
        now = datetime.datetime.now()
        past_datetime = now - datetime.timedelta( days=settings_app.EXPIRY_DAYS )
        log.debug( 'past_datetime, `%s`' % past_datetime )
        return past_datetime

    def clean_request( self, request ):
        """ Removes identifying data.
            Called by clean_patron_data() """
        cleaned_dct = {}
        existing_patron_dct = json.loads( request.patron_info )
        for (key, value) in existing_patron_dct.items():
            if key in settings_app.DEMOGRAPHIC_CATEGORIES:
                cleaned_dct[key] = value
        if cleaned_dct != existing_patron_dct:
            log.debug( 'saving cleaned data' )
            request.save()
        else:
            log.debug( 'data already cleaned' )
        return

    ## end class ExpirationManager()


if __name__ == '__main__':
    exp_mngr = ExpirationManager()
    ExpirationManager.clean_patron_data()
    log.debug( 'complete' )
