""""
Contains code to call the Sierra patron-api.
The resulting 'ptype' is checked for validity.
Triggered initially by views.shib_login()
"""

import json, logging, os, pprint, time
import requests
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class PatronApiHelper( object ):
    """ Assists getting and evaluating patron-api data.
        Used by ShibChecker(). """

    def __init__( self ):
        self.PATRON_API_URL = settings_app.PATRON_API_URL
        self.PATRON_API_BASIC_AUTH_USERNAME = settings_app.PATRON_API_BASIC_AUTH_USERNAME
        self.PATRON_API_BASIC_AUTH_PASSWORD = settings_app.PATRON_API_BASIC_AUTH_PASSWORD
        self.PATRON_API_LEGIT_PTYPES = settings_app.PATRON_API_LEGIT_PTYPES
        self.ptype_validity = False
        self.id_check = False

    def process_barcode( self, patron_barcode, shortlink ):
        """ Hits patron-api to extract sierra-patron-id, and to check the p-type.
            Called by lib/shib_helper.ShibChecker.authorize() """
        papi_dct = self.hit_api( patron_barcode )
        if papi_dct is False:
            return
        self.id_check = self.extract_sierra_patron_id( papi_dct, shortlink )
        if self.id_check is False:
            return
        self.ptype_validity = self.check_ptype( papi_dct )
        if self.ptype_validity is False:
            return
        return

    def hit_api( self, patron_barcode ):
        """ Runs web-query.
            Called by process_barcode() """
        try:
            r = requests.get( self.PATRON_API_URL, params={'patron_barcode': patron_barcode}, timeout=5, auth=(self.PATRON_API_BASIC_AUTH_USERNAME, self.PATRON_API_BASIC_AUTH_PASSWORD) )
            r.raise_for_status()  # will raise an http_error if not 200
            log.debug( 'r.content, ```%s```' % str(r.content) )
        except:
            log.exception( 'problem getting data for patron_barcode, `%s`; traceback follows; will try a 2nd time' % patron_barcode  )
            time.sleep( 1 )
            try:
                r = requests.get( self.PATRON_API_URL, params={'patron_barcode': patron_barcode}, timeout=5, auth=(self.PATRON_API_BASIC_AUTH_USERNAME, self.PATRON_API_BASIC_AUTH_PASSWORD) )
            except:
                log.exception( 'problem on 2nd try getting patron-api data; traceback follows; return `False`' )
                return False
        return r.json()

    # def hit_api( self, patron_barcode ):
    #     """ Runs web-query.
    #         Called by process_barcode() """
    #     try:
    #         r = requests.get( self.PATRON_API_URL, params={'patron_barcode': patron_barcode}, timeout=10, auth=(self.PATRON_API_BASIC_AUTH_USERNAME, self.PATRON_API_BASIC_AUTH_PASSWORD) )
    #         r.raise_for_status()  # will raise an http_error if not 200
    #         log.debug( 'r.content, ```%s```' % str(r.content) )
    #     except Exception as e:
    #         log.error( 'exception, `%s`' % str(e) )
    #         return False
    #     return r.json()

    def extract_sierra_patron_id( self, papi_dct, shortlink ):
        """ Extracts and saves sierra-patron-id if possible.
            Calle by process_barcode() """
        id_check = False
        try:
            item_request = ItemRequest.objects.get( short_url_segment=shortlink )
            patron_dct = json.loads( item_request.patron_info )
            log.debug( 'patron_dct, ```%s```' % pprint.pformat(patron_dct) )
            if 'sierra_patron_id' not in patron_dct.keys():
                sierra_patron_id = papi_dct['response']['record_']['value'][1:]  # strips initial character from, eg, '=1234567'
                patron_dct['sierra_patron_id'] = sierra_patron_id
                item_request.patron_info = json.dumps( patron_dct, sort_keys=True, indent=2 )
                item_request.save()
                id_check = True
        except:
            log.exception( 'problem extracting or saving sierra-patron-id; traceback follows; returning `False`' )
        log.debug( f'id_check, `{id_check}`' )
        return id_check

    def check_ptype( self, api_dct ):
        """ Sees if ptype is valid.
            Called by process_barcode() """
        return_val = False
        patron_ptype = api_dct['response']['p_type']['value']
        if patron_ptype in self.PATRON_API_LEGIT_PTYPES:
            return_val = True
        log.debug( 'ptype check, `%s`' % return_val )
        return return_val

    ## end class PatronApiHelper
