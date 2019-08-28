""""
Contains code to:
- call the availability-api to get the item-id needed to make the Sierra request.
- make the Sierra request.
Triggered initially by views.processor()
"""

import json, logging, os, pprint
import requests
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.lib.iii_account import IIIAccount
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class Millennium( object ):
    """ Gets item_id and places hold. """

    def __init__( self ):
        self.AVAILABILITY_API_URL_ROOT = settings_app.AVAILABILITY_API_URL_ROOT
        self.LOCATION_CODE = settings_app.HAY_LOCATION_CODE
        self.item_bib = ''
        self.item_barcode = ''
        self.item_id = None
        self.patron_barcode = ''
        self.patron_login_name = ''
        self.hold_status = None  # updated in call_place_hold()

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
        self.patron_login_name = patron_dct['firstname']
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

    # def hit_availability_api( self, bibnum ):
    #     """ Returns availability-api dct.
    #         Called by get_item_id() """
    #     avail_dct = {}
    #     availability_api_url = '%sbib/%s' % ( self.AVAILABILITY_API_URL_ROOT, bibnum )
    #     log.debug( 'availability_api_url, ```%s```' % availability_api_url )
    #     try:
    #         r = requests.get( availability_api_url )
    #         avail_dct = r.json()
    #         log.debug( 'partial availability-api-response, `%s`' % pprint.pformat(avail_dct)[0:200] )
    #     except:
    #         log.exception( 'problem hitting availability-service; traceback follows, but processing will continue' )
    #     log.debug( 'avail_dct, ```%s```' % avail_dct )
    #     return avail_dct

    def hit_availability_api( self, bibnum ):
        """ Returns availability-api dct.
            Called by get_item_id() """
        avail_dct = {}
        # availability_api_url = '%sbib/%s' % ( self.AVAILABILITY_API_URL_ROOT, bibnum )
        availability_api_url = f'{self.AVAILABILITY_API_URL_ROOT}/v2/bib_items/{bibnum}/'
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

    # def extract_item_id( self, avail_dct, item_barcode ):
    #     """ Uses barcode to get item_id.
    #         Called by get_item_id() """
    #     item_id = None
    #     try:
    #         results = avail_dct['response']['backend_response']
    #         for result in results:
    #             items = result['items_data']
    #             for item in items:
    #                 if item_barcode == item['barcode']:
    #                     item_id = item['item_id'][:-1]  # removes trailing check-digit
    #     except:
    #         log.exception( 'problem getting item_id; traceback follows, but processing will continue' )
    #     log.debug( 'item_id, `%s`' % item_id )
    #     return item_id

    def call_place_hold( self ):
        """ Calls lib to place hold.
            Called by views.processor()
            Elements needed for hold: user_name, user_barcode, item_bib, item_id, pickup_location """
        status = 'init'
        try:
            jos_sess = IIIAccount( name=self.patron_login_name, barcode=self.patron_barcode )
            jos_sess.login()
            log.debug( f'jos_sess, ```{jos_sess}```' )
            hold_result_dct = jos_sess.place_hold( bib=self.item_bib, item=self.item_id, pickup_location=self.LOCATION_CODE )
            log.debug( f'hold_result_dct, ```{hold_result_dct}```' )
            jos_sess.logout()
            self.hold_status = 'request_placed'
        except:
            log.exception( 'problem placing hold; traceback follows, but processing will continue to try another iii-logout...' )
            try:
                jos_sess.logout()
                log.warning( 'jos_sess.logout() succeeded on exception catch' )
            except:
                log.exception( 'problem with 2nd iii-logout attempt; traceback follows, but processing will continue...' )
        log.debug( f'self.hold_status, `{self.hold_status}`' )
        return

    ## end class Millennium()

