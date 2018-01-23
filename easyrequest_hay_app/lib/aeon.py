# -*- coding: utf-8 -*-

import datetime, json, urllib
from easyrequest_hay_app.models import ItemRequest


class AeonUrlBuilder( object ):

    def __init__( self ):
        self.aeon_root_url = 'https://brown.aeon.atlas-sys.com/logon/?Action=10&Form=30'
        self.aeon_params = {
            'ReferenceNumber': '',  # item_bib
            'ItemTitle': '',
            'ItemAuthor': '',
            'ItemPublisher': '',
            'CallNumber': '',
            'Location': '',
            'SpecialRequest': 'Not needed in next 2 weeks, so not auto-requested through Millennium.'  # notes for staff; default
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
        self.aeon_params['ReferenceNumber'] = request_dct['item_bib']
        self.aeon_params['ItemTitle'] = request_dct['item_title']
        self.aeon_params['ItemAuthor'] = request_dct['item_author']
        self.aeon_params['ItemPublisher'] = request_dct['item_publisher']
        self.aeon_params['CallNumber'] = request_dct['item_callnumber']
        self.aeon_params['Location'] = request_dct['item_location']
        aeon_url = '%s&%s' % ( self.aeon_root_url, urllib.parse.urlencode(self.aeon_params) )
        return aeon_url
