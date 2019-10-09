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
from requests.auth import HTTPBasicAuth


log = logging.getLogger(__name__)


class SierraHelper( object ):
    """ Gets item_id and places hold. """

    def __init__( self ):
        # self.AVAILABILITY_API_URL_ROOT = settings_app.AVAILABILITY_API_URL_ROOT
        # self.LOCATION_CODE = ''
        # self.SIERRA_API_URL_ROOT = ''
        # self.SIERRA_API_KEY = ''
        # self.SIERRA_API_SECRET = ''
        self.item_dct = {}  # populated by prep_item_data() for use in aeon.build_aeon_url()
        self.item_bib = ''
        self.item_barcode = ''
        self.item_id = None
        self.patron_barcode = ''
        # self.patron_login_name = ''
        self.patron_sierra_id = ''
        self.hold_status = 'problem'  # updated in place_hold()

    def prep_item_data( self, shortlink ):
        """ Preps item-data from item_request.
            Called by views.processor() """
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        self.item_dct = item_dct = json.loads( item_request.full_url_params )
        log.debug( 'item_dct, ```%s```' % pprint.pformat(item_dct) )
        patron_dct = json.loads( item_request.patron_info )
        log.debug( 'patron_dct, ```%s```' % pprint.pformat(patron_dct) )
        self.item_bib = item_dct['item_bib']
        self.item_barcode = item_dct['item_barcode']
        self.patron_barcode = patron_dct['patron_barcode']
        # self.patron_login_name = patron_dct['firstname']
        self.patron_sierra_id = patron_dct['sierra_patron_id']
        self.get_item_id()
        log.debug( 'bib, `%s`; item_barcode, `%s`; patron_barcode, `%s`' % (self.item_bib, self.item_barcode, self.patron_barcode) )
        log.debug( 'instance-info, ```%s```' % pprint.pformat(self.__dict__) )
        return

    def get_item_id( self ):
        """ Calls availability-api to get the item-id.
            Called by prep_item_data() """
        avail_dct = self.hit_availability_api( self.item_bib )
        if avail_dct:
            self.item_id = self.extract_item_id( avail_dct, self.item_barcode )
        log.debug( 'item_id, `%s`' % self.item_id )
        return

    def hit_availability_api( self, bibnum ):
        """ Returns availability-api dct.
            Called by get_item_id() """
        avail_dct = {}
        # availability_api_url = '%sbib/%s' % ( self.AVAILABILITY_API_URL_ROOT, bibnum )
        availability_api_url = f'{settings_app.AVAILABILITY_API_URL_ROOT}/v2/bib_items/{bibnum}/'
        log.debug( 'availability_api_url, ```%s```' % availability_api_url )
        try:
            r = requests.get( availability_api_url, headers={'user-agent': settings_app.USER_AGENT}, timeout=15 )
            avail_dct = r.json()
            log.debug( 'partial availability-api-response, `%s`' % pprint.pformat(avail_dct)[0:200] )
        except:
            log.exception( 'problem hitting availability-service; traceback follows, but processing will continue' )
        log.debug( 'avail_dct, ```%s```' % avail_dct )
        return avail_dct

    def extract_item_id( self, avail_dct, item_barcode ):
        """ Uses barcode to get item_id.
            Called by get_item_id() """
        item_id = None
        try:
            items = avail_dct['response']['items']
            for item in items:
                if item_barcode == item['barcode']:
                    item_id = item['item_id'][:-1]  # removes trailing check-digit
        except:
            log.exception( 'problem getting item_id; traceback follows, but processing will continue' )
        log.debug( 'item_id, `%s`' % item_id )
        return item_id

    def manage_place_hold( self ):
        """ Gets token and places hold.
            Called by views.processor() """
        token = self.get_token()
        self.place_hold( token )
        log.debug( 'manage_place_hold() done.' )
        return

    def get_token( self ):
        token = 'init'
        token_url = f'{settings_app.SIERRA_API_ROOT_URL}/token'
        log.debug( 'token_url, ```%s```' % token_url )
        try:
            r = requests.post( token_url,
                auth=HTTPBasicAuth( settings_app.SIERRA_API_KEY, settings_app.SIERRA_API_SECRET ),
                timeout=20 )
            log.debug( 'token r.content, ```%s```' % r.content )
            token = r.json()['access_token']
            log.debug( 'token, ```%s```' % token )
            return token
        except:
            log.exception( 'problem getting token; traceback follows' )
            raise Exception( 'exception getting token' )

    def place_hold( self, token ):
        log.info( 'placing hold' )
        request_url = f'{settings_app.SIERRA_API_ROOT_URL}/patrons/{self.patron_sierra_id}/holds/requests'
        custom_headers = {'Authorization': f'Bearer {token}' }
        log.debug( f'custom_headers, ```{custom_headers}```' )
        # payload = '{"recordType": "i", "recordNumber": 10883346, "pickupLocation": "r0001", "note": "birkin_api_testing"}'  # ZMM item, https://library.brown.edu/availability_api/v2/bib_items/b1815113/
        payload_dct = {
            'recordType': 'i',
            'recordNumber': int(self.item_id[1:]),  # removes initial 'i'
            'pickupLocation': settings_app.HAY_LOCATION_CODE,
            'note': 'easyrequest_hay_api_request'
            }
        log.debug( f'payload_dct, ```{pprint.pformat(payload_dct)}```' )
        payload = json.dumps( payload_dct )
        log.debug( f'payload-json-string, ```{payload}```' )
        try:
            r = requests.post( request_url, headers=custom_headers, data=payload, timeout=30 )
            log.info( f'r.status_code, `{r.status_code}`' )
            log.info( f'r.url, `{r.url}`' )
            log.info( f'r.content, `{r.content}`' )
            if r.status_code == 200:
                self.hold_status = 'hold_placed'
        except:
            log.exception( 'problem hitting api to request item; traceback follows' )
        log.debug( f'hold_status, `{self.hold_status}`' )
        return

    def run_problem_check( self ):
        if self.hold_status == 'hold_placed':
            return 'all good!'
        ## query all requests for past half-hour where title == self.title
        ## loop through them
            ## if the admin-note indicates that a staff email was sent, enter into the current ItemRequest the admin note "Staff email already sent"



    ## end class SierraHelper()
