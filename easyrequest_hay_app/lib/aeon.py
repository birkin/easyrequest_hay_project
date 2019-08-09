# -*- coding: utf-8 -*-

""""
Builds the Aeon url the user will be redirected to.
"""

import datetime, json, logging, urllib
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class AeonUrlBuilder( object ):

    def __init__( self ):
        self.aeon_root_url = 'https://brown.aeon.atlas-sys.com/logon/?Action=10&Form=30'
        self.aeon_params = {
            'CallNumber': '',
            'ItemAuthor': '',
            'ItemPublisher': '',
            'ItemTitle': '',
            'Location': '',
            'ReferenceNumber': '',  # item_bib
            'SpecialRequest': ''  # notes for staff; default
        }

    def make_millennium_note( self, item_id ):
        """ Sets the staff note when an item has been auto-requested through Millennium.
            Called by views.processor() """
        now_str = datetime.datetime.now().strftime( '%Y-%b-%d-%a-%I:%M:%S%p' )  # '2018-Jan-23-Tue-03:41:35PM'
        self.aeon_params['SpecialRequest'] = 'Auto-requested via easyRequest-Hay at `%s`; item_id, `%s`' % ( now_str, item_id )
        return

    def build_aeon_url( self, shortlink ):
        """ Saves data.
            Called by views.time_period() """
        itmrqst = ItemRequest.objects.get( short_url_segment=shortlink )
        request_dct = json.loads( itmrqst.full_url_params )
        self.update_params( request_dct )
        aeon_url = '%s&%s' % ( self.aeon_root_url, urllib.parse.urlencode(self.aeon_params) )
        log.debug( 'aeon_url, ```%s```' % aeon_url )
        return aeon_url

    def update_params( self, request_dct ):
        """ Updates data.
            Called by build_aeon_url() """
        self.aeon_params['CallNumber'] = request_dct['item_callnumber']
        self.aeon_params['ItemAuthor'] = request_dct['item_author']
        self.aeon_params['ItemPublisher'] = request_dct['item_publisher']
        self.aeon_params['ItemTitle'] = request_dct['item_title']
        self.aeon_params['Location'] = request_dct['item_location']
        self.aeon_params['ReferenceNumber'] = request_dct['item_bib']
        return

    ## end class AeonUrlBuilder()
