""""
TODO: remove this and the single call to it.
This was originally used when lots of data was stored in the session,
  but that architecture was replaced by quickly creating a shortlink and storing essential data temporarily in the db.
Triggered initially by views.confirm()
"""

import logging, pprint


log = logging.getLogger(__name__)


class SessionHelper( object ):
    """ Helps to initialize and manage `request.session`. """

    def __init__( self ):
        """ Non-obvious usage...
            - patron_full_name, for email
            - patron_las_name, for possible second josiah-api attempt if default shib firstname fails
        """
        self.item_info_keys = [ 'item_title', 'item_bib', 'item_id', 'item_barcode', 'item_callnumber', 'item_pickup_location' ]
        '''patron_full_name for email'''
        self.patron_info_keys = [ 'patron_full_name', 'patron_last_name', 'patron_email', 'patron_barcode_login_name', 'patron_barcode_login_barcode' ]
        self.other_info_keys = ['']

    def initialize_session( self, request ):
        """ Initializes session.
            Called by views.time_period() """
        for key in self.item_info_keys:
            request.session[key] = ''
        for key in self.patron_info_keys:
            request.session[key] = ''
        for key in self.other_info_keys:
            request.session[key] = ''
        log.debug( 'request.session after initialization, ```%s```' % pprint.pformat(request.session.items()) )
        return
