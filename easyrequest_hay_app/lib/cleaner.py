# -*- coding: utf-8 -*-

import datetime, json, logging, os, sys
import django

## configure django paths
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
cwd = os.getcwd()  # this assumes the cron call has cd-ed into the project directory
if cwd not in sys.path:
    sys.path.append( cwd )
django.setup()

## ok, now django-related imports will work
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.models import ItemRequest


logging.basicConfig(
    filename=os.environ['EZRQST_HAY__LOG_PATH'],
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)


class ExpirationManager( object ):
    """ Manages removal of personally-identifying-information. """

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
        existing_patron_dct = self.load_existing_patron_data( request )
        for (key, value) in existing_patron_dct.items():
            if key in settings_app.DEMOGRAPHIC_CATEGORIES:
                cleaned_dct[key] = value
        if cleaned_dct != existing_patron_dct:
            log.debug( 'id, `%s`; saving cleaned data' % request.id )
            request.patron_info = json.dumps( cleaned_dct, sort_keys=True, indent=2 )
            request.save()
        else:
            log.debug( 'id, `%s`; data already cleaned' % request.id )
        return

    def load_existing_patron_data( self, request ):
        """ Returns data-dct or empty-dct.
            Called by clean_request() """
        try:
            existing_patron_dct = json.loads( request.patron_info )
        except TypeError as e:  # occurs when field is empty (TODO: filter for non-empty fields)
            existing_patron_dct = {}
        return existing_patron_dct

    ## end class ExpirationManager()


if __name__ == '__main__':
    exp_mngr = ExpirationManager()
    exp_mngr.clean_patron_data()
    log.debug( 'complete' )
