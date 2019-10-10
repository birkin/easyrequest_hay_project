""""
Contains code for checking whether a 'problem' email needs to be sent to staff, and if so, sends the email.
Triggered initially by views.processor()
"""

import json, logging

from django.core.mail import EmailMessage
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class Emailer:

    def __init__( self ):
        self.email_subject = 'easyrequest_hay auto-annex-request unsuccessful'

    # def run_send_check( self, millennium_item_id, millennium_hold_status, shortlink ):
    #     """ Checks to see if problem-email to staff needs to be sent, and sends it.
    #         Called by views.processor() """
    #     if millennium_item_id and millennium_hold_status:  ## happy path
    #         log.debug( 'no need to send staff email' )
    #         return
    #     else:
    #         itmrqst = ItemRequest.objects.get( short_url_segment=shortlink )
    #         item_json = itmrqst.full_url_params  # json
    #         patron_json = self.extract_basic_patron_info( json.loads(itmrqst.patron_info) )
    #         self.email_staff( patron_json, item_json )
    #         log.debug( 'email attempt complete' )
    #     return

    # def extract_basic_patron_info( self, patron_dct ):
    #     """ Returns subset of captured patron data.
    #         Called by run_send_check() """
    #     sub_dct = {
    #         'HTTP_SHIBBOLETH_BROWNTYPE': patron_dct['HTTP_SHIBBOLETH_BROWNTYPE'],
    #         'HTTP_SHIBBOLETH_DEPARTMENT': patron_dct['HTTP_SHIBBOLETH_DEPARTMENT'],
    #         'email': patron_dct['email'],
    #         'eppn': patron_dct['eppn'],
    #         'firstname': patron_dct['firstname'],
    #         'lastname': patron_dct['lastname'],
    #         'patron_barcode': patron_dct['patron_barcode']
    #         }
    #     patron_json = json.dumps( sub_dct, sort_keys=True, indent=2 )
    #     log.debug( f'patron_json, ```{patron_json}```' )
    #     return patron_json

    def email_staff( self, patron_json, item_json ):
        """ Emails staff problem alert.
            Called by run_send_check() """
        try:
            body = self.build_email_body( patron_json, item_json )
            # log.debug( f'body, ```{body}```' )
            ffrom = settings_app.STAFF_EMAIL_FROM  # `from` reserved
            to = settings_app.STAFF_EMAIL_TO  # list
            extra_headers = { 'Reply-To': settings_app.STAFF_EMAIL_REPLYTO }
            email = EmailMessage( self.email_subject, body, ffrom, to, headers=extra_headers )
            email.send()
            log.debug( 'mail sent' )
        except Exception as e:
            log.exception( 'exception sending email; traceback follows, but processing continues' )
        return

    def build_email_body( self, patron_json, item_json ):
        """ Prepares and returns email body.
            Called by email_staff().
            TODO: use render_to_string & template. """
        body = f'''Greetings Hay Staff,

This is an automated email from the easyRequest_Hay web-app.

This was sent because a patron requested an AnnexHay item, but the item could not be auto-requested (behind-the-scenes) from Sierra.

The patron landed at the Aeon request form (where a staff note about the failure was auto-inserted).

(Note that the patron may or may not have actually submitted the Aeon request.)

FYI, the patron info...

{patron_json}

...and the item info...

{item_json}

::: END :::
'''
        return body

        ## end def build_email_body()

    ## end class Emailer
