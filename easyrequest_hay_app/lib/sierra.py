""""
Contains code to:
    - call APIs to prepare the data for the Sierra API call
        - availability-api: to get the item-id
        - patron-api to get the patron-id
    - hit the Sierra request-API
    - evaluate whether a staff "problem-email" should go out
Triggered initially by views.processor()
"""

import json, logging, os, pprint
import requests
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class SierraHelper( object ):
    """ Gets item_id and places hold. """

    def __init__( self ):
        self.AVAILABILITY_API_URL_ROOT = ''
        self.LOCATION_CODE = ''
        self.SIERRA_API_URL_ROOT = ''
        self.SIERRA_API_KEY = ''
        self.SIERRA_API_SECRET = ''

        self.item_bib = ''
        self.item_barcode = ''
        self.item_id = None
        self.patron_barcode = ''
        # self.patron_login_name = ''
        self.patron_sierra_id = ''
        self.hold_status = ''  # updated in place_hold()

    def prep_item_data( self, shortlink ):
        """ Preps item-data from item_request.
            Called by views.processor() """
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        item_dct = json.loads( item_request.full_url_params )
        log.debug( 'item_dct, ```%s```' % pprint.pformat(item_dct) )
        patron_dct = json.loads( item_request.patron_info )
        log.debug( 'patron_dct, ```%s```' % pprint.pformat(patron_dct) )
        self.item_bib = item_dct['item_bib']
        self.item_barcode = item_dct['item_barcode']
        self.patron_barcode = patron_dct['patron_barcode']
        # self.patron_login_name = patron_dct['firstname']
        self.patron_sierra_id = patron_dct['sierra_patron_id']
        log.debug( 'bib, `%s`; item_barcode, `%s`; patron_barcode, `%s`' % (self.item_bib, self.item_barcode, self.patron_barcode) )
        log.debug( 'instance-info, ```%s```' % pprint.pformat(self.__dict__) )
        return

    # def manage_place_hold( self )

    def get_token( self ):
        token = 'init'
        token_url = f'{SIERRA_API_URL}/token'
        log.debug( 'token_url, ```%s```' % token_url )
        try:
            r = requests.post( token_url,
                auth=HTTPBasicAuth( SIERRA_API_USERNAME, SIERRA_API_PASSWORD ),
                timeout=20 )
            log.debug( 'token r.content, ```%s```' % r.content )
            token = r.json()['access_token']
            log.debug( 'token, ```%s```' % token )
        except:
            log.exception( 'problem getting token; traceback follows' )
            raise Exception( 'exception getting token' )

    def place_hold( self ):
        log.info( 'placing hold' )
        request_url = f'{SIERRA_API_URL}/patrons/{SIERRA_PATRON_ID}/holds/requests'
        custom_headers = {'Authorization': f'Bearer {token}' }
        payload = '{"recordType": "i", "recordNumber": 10883346, "pickupLocation": "r0001", "note": "birkin_api_testing"}'  # ZMM item, https://library.brown.edu/availability_api/v2/bib_items/b1815113/
        try:
            r = requests.post( request_url, headers=custom_headers, data=payload, timeout=30 )
            log.info( f'r.status_code, `{r.status_code}`' )
            log.info( f'r.url, `{r.url}`' )
            log.info( f'r.content, `{r.content}`' )
            self.hold_status = 'request_placed'
        except:
            log.exception( 'problem hitting api to request item; traceback follows' )
        log.debug( f'hold_status, `{self.hold_status}`' )
        return
