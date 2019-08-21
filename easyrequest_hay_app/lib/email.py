""""
Contains code for checking whether a 'problem' email needs to be sent to staff, and if so, sends the email.
Triggered initially by views.processor()
"""

import logging


log = logging.getLogger(__name__)


class Emailer():
    """ Contains helpers for views.confirm() for handling GET. """

    def __init__( self ):
        pass


    def run_send_check( self, patron_dct, item_dct, millennium.id, millennium.hold_status ):
        """ Checks to see if problem-email to staff needs to be sent, and sends it.
            Called by views.processor() """
        pass


    def email_patron( self, patron_email, patron_name, item_title, item_callnumber, item_bib, item_id, patron_barcode, item_barcode, pickup_location_code ):
        """ Emails patron confirmation.
            Called by views.processor() """
        try:
            pickup_location_display = self.prep_pickup_location_display( pickup_location_code )
            body = self.build_email_body( patron_name, item_title, item_callnumber, item_bib, item_id, patron_barcode, item_barcode, pickup_location_display )
            ffrom = self.EMAIL_FROM  # `from` reserved
            to = [ patron_email ]
            extra_headers = { 'Reply-To': self.EMAIL_REPLY_TO }
            email = EmailMessage( self.email_subject, body, ffrom, to, headers=extra_headers )
            email.send()
            log.debug( 'mail sent' )
        except Exception as e:
            log.error( 'Exception sending email, `%s`' % unicode(repr(e)) )
        return

    def prep_pickup_location_display( self, pickup_location_code ):
        """ Returns pickup-location-display string.
            Called by email_patron() """
        pic_loc = PickupLocation()
        pickup_location_display = pic_loc.code_to_display_dct[ pickup_location_code ]
        return pickup_location_display

    def build_email_body( self,  patron_name, item_title, item_callnumber, item_bib, item_id, patron_barcode, item_barcode, pickup_location_display ):
        """ Prepares and returns email body.
            Called by email_patron().
            TODO: use render_to_string & template. """
        body = '''Greetings %s,

This is a confirmation of your request for the item...

Title: %s
Call Number: %s

Items requested form the Annex are generally available in 1 business day. You will receive an email when the item is available for pickup at the %s.

If you have questions, feel free to email %s or call %s, and refer to...

- Bibliographic #: "%s"
- Item #: "%s"
- User barcode: "%s"
- Item barcode: "%s"

::: Annex Item-Requesting -- a service of the Brown University Library :::
''' % (
            patron_name,
            item_title,
            item_callnumber,
            pickup_location_display,
            self.EMAIL_GENERAL_HELP,
            self.PHONE_GENERAL_HELP,
            item_bib,
            item_id,
            patron_barcode,
            item_barcode
            )
        return body

        ## end def build_email_body()

    ## end class Emailer()
