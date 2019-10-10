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
        self.item_request = None
        self.item_dct = {}  # populated by prep_item_data() for use in aeon.build_aeon_url()
        self.item_bib = ''
        self.item_barcode = ''
        self.item_id = None
        self.item_title = ''
        self.patron_barcode = ''
        # self.patron_login_name = ''
        self.patron_sierra_id = ''
        self.hold_status = 'problem'  # updated in place_hold()

    def prep_item_data( self, shortlink ):
        """ Preps item-data from item_request.
            Called by views.processor() """
        self.item_request = ItemRequest.objects.get( short_url_segment=shortlink )

        self.item_dct = item_dct = json.loads( self.item_request.full_url_params )
        log.debug( 'item_dct, ```%s```' % pprint.pformat(item_dct) )
        patron_dct = json.loads( self.item_request.patron_info )
        log.debug( 'patron_dct, ```%s```' % pprint.pformat(patron_dct) )
        self.item_bib = item_dct['item_bib']
        self.item_barcode = item_dct['item_barcode']
        self.item_title = item_dct['item_title']
        self.patron_barcode = patron_dct['patron_barcode']
        # self.patron_login_name = patron_dct['firstname']
        self.patron_sierra_id = patron_dct['sierra_patron_id']
        self.get_item_id()
        log.debug( 'bib, `%s`; item_barcode, `%s`; patron_barcode, `%s`' % (self.item_bib, self.item_barcode, self.patron_barcode) )
        log.debug( 'SierraHelper instance-info, ```%s```' % pprint.pformat(self.__dict__) )
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
        """ Gets token.
            Called by manage_place_hold() """
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
        """ Attempts to place hold via sierra api.
            Called by manage_place_hold() """
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

    def send_email_check( self ):
        """ Evaluates whether an email needs to be sent.
            Called by views.processor() """
        return_check = False
        if self.hold_status == 'hold_placed':
            pass
        else:  # hold-try failed, but was an email already recently sent?
            now_time = datetime.datetime.now()
            half_hour_ago =  now_time - datetime.timedelta( minutes=30 )
            ## query all requests for past half-hour where past-request.item-id == current-item.item-id
            possible_duplicates = ItemRequest.objects.filter( item_title=self.item_title, create_datetime__gte=half_hour_ago )  # add `, patron_info__isnull=False`? I don't think so, because this path assumes shib, so there should always be patron info
            ## loop through them
            recent_email_sent = False
            for poss_dup in possible_duplicates:
                poss_dup_item_dct = json.loads( poss_dup.full_url_params )
                poss_dup_patron_dct = json.loads( poss_dup.patron_info )
                if poss_dup_item_dct['item_barcode'] == self.item_barcode:
                    if poss_dup_patron_dct['patron_barcode'] == self.patron_barcode:
                        ## ok poss_dup _is_ a duplicate
                        if 'will send staff-email' in poss_dup.admin_notes.lower():
                            recent_email_sent = True
                            updated_notes = 'Not sending staff-email re unable-to-request-via-sierra; already sent.' + '\n\n' + self.item_request.admin_notes
                            self.item_request.admin_notes = updated_notes.strip()
                            break
            if recent_email_sent is False:
                return_check = True
                updated_notes = 'Will send staff-email re unable-to-request-via-sierra.' + '\n\n' + self.item_request.admin_notes
                self.item_request.admin_notes = updated_notes.strip()
            log.debug( f'updated admin notes, ```{self.item_request.admin_notes}```' )
        log.debug( f'return_check, `{return_check}`' )
        return return_check

    ## end class SierraHelper()
