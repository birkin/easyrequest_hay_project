# -*- coding: utf-8 -*-

import json, logging, os


log = logging.getLogger(__name__)


class PickupLocation( object ):
    """ Holds pickup-location info for display, and for placing hold.
        Called by models.LoginHelper.__init__(),
                  models.Processor.prep_pickup_location_display(), and
                  models.ShibLogoutHelper.build_redirect_url() """

    def __init__( self ):
        """ dct structure example: { 'ROCK': {'code': 'r0001', 'display': 'Rockefeller Library'}, etc... } """
        self.pickup_location_dct = json.loads( os.environ['EZRQST_HAY__PICKUP_LOCATION_JSON'] )
        self.code_to_display_dct = {}
        self.process_dct()

    def process_dct( self ):
        """ Creates another dct from the env json like: { 'sci': 'Sciences Library', 'h0001': 'John Hay Library', etc... }.
            Triggered by __init__() """
        new_dct = {}
        for ( key, val ) in self.pickup_location_dct.items():
            # log.debug( 'key, `%s`' % key ); log.debug( 'val, `%s`' % val )
            new_key = val['code']
            new_val = val['display']
            new_dct[ new_key ] = new_val
        log.debug( 'new_dct, `%s`' % new_dct )
        self.code_to_display_dct = new_dct

    # end class PickupLocation
