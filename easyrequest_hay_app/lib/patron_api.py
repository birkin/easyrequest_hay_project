# -*- coding: utf-8 -*-

import json, logging, os, pprint
import requests
from easyrequest_hay_app import settings_app


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
        # self.patron_name = None  # will be last, first middle (used only by BarcodeHandler)
        # self.patron_email = None  # will be lower-case (used only by BarcodeHandler)
        # self.process_barcode( patron_barcode )

    # def process_barcode( self, patron_barcode ):
    #     """ Hits patron-api and populates attributes.
    #         Called by __init__(); triggered by BarcodeHandlerHelper.authorize() and eventually a shib function. """
    #     api_dct = self.hit_api( patron_barcode )
    #     if api_dct is False:
    #         return
    #     self.ptype_validity = self.check_ptype( api_dct )
    #     if self.ptype_validity is False:
    #         return
    #     self.patron_name = api_dct['response']['patrn_name']['value']  # last, first middle
    #     self.patron_email = api_dct['response']['e-mail']['value'].lower()
    #     return

    def process_barcode( self, patron_barcode ):
        """ Hits patron-api and populates attributes.
            Called by lib/shib_helper.ShibChecker.authorize() """
        api_dct = self.hit_api( patron_barcode )
        if api_dct is False:
            return
        self.ptype_validity = self.check_ptype( api_dct )
        if self.ptype_validity is False:
            return
        # self.patron_name = api_dct['response']['patrn_name']['value']  # last, first middle
        # self.patron_email = api_dct['response']['e-mail']['value'].lower()
        return

    def hit_api( self, patron_barcode ):
        """ Runs web-query.
            Called by process_barcode() """
        try:
            r = requests.get( self.PATRON_API_URL, params={'patron_barcode': patron_barcode}, timeout=5, auth=(self.PATRON_API_BASIC_AUTH_USERNAME, self.PATRON_API_BASIC_AUTH_PASSWORD) )
            r.raise_for_status()  # will raise an http_error if not 200
            log.debug( 'r.content, ```%s```' % str(r.content) )
        except Exception as e:
            log.error( 'exception, `%s`' % str(e) )
            return False
        return r.json()

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
