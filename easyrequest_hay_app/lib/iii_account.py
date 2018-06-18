# -*- coding: utf-8 -*-

import logging, os, pprint, time
import requests
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class IIIAccount():

    def __init__(self, name, barcode):
        self.name = name
        self.barcode = barcode
        self.patron_id = None
        self.session_id = None
        self.cookies = None
        self.opac_url = os.environ['EZRQST_HAY__OPAC_BASE_URL']
        self.request_base = self.opac_url + 'search~S7?/.{{bib}}/.{{bib}}/1%2C1%2C1%2CB/request~{{bib}}'  # updated via get_items()
        self.session = requests.Session()
        self.session.verify = False

    def login(self):
        payload = {
            'name' : self.name,
            'code' : self.barcode,
            'pat_submit':'xxx'
        }
        """
        extpatid:
        extpatpw:
        name:
        code:
        pat_submit:xxx
        """
        out = {
               'username': self.name,
               'authenticated': False,
               'url': None}
        url = self.opac_url + 'patroninfo'
        rsp = self.session.post(url, data=payload, allow_redirects=True)
        doc = BeautifulSoup( rsp.content.decode('utf-8') )
        login_error = doc.find( "span", class_="login_error" )  # <span class="login_error"> exists if login fails
        if (login_error):
            raise Exception("Login failed.")
        else:
            out['authenticated'] = True
            url = rsp.url
            out['url'] = url
            out['patron_id'] = url.split('/')[-2]
            self.patron_id = out['patron_id']
            log.info("Patron {} authenticated.".format({self.patron_id}))
        log.debug( 'login-result, ```%s```' % pprint.pformat(out) )
        return out

    def logout(self):
        """
        This seems to be pretty straight forward.  Just hit the url and session
        cookies.  Then carry on.
        """
        url = self.opac_url + 'logout~S7?'
        rsp = self.session.get(url)
        #Add check to verify text or url is what is expected.
        return True

    def _validate_session(self, content):
        if 'your validation has expired' in content.lower():
            raise Exception("Validation expired.")

    def get_holds(self):
        """
        Return a list of holds for a user.
        """
        url = self.opac_url + 'patroninfo~S7/%s/holds' % self.patron_id
        rsp = self.session.get(url)
        #error checking to see if we logged in?
        content = rsp.content
        self._validate_session(content)
        holds = self._parse_holds_list(content)
        return holds

    def _parse_holds_list(self, content):
        """ Parses holds html.
            Called by get_holds() """
        # content = content if type(content) == unicode else content.decode( 'utf-8', 'replace' )
        content = content if type(content) == str else content.decode( 'utf-8', 'replace' )
        ( doc, holds ) = ( BeautifulSoup(content), [] )
        hold_rows = doc.find_all( 'tr', class_='patFuncEntry' )
        for row in hold_rows:
            holds.append( {
                # 'key': unicode( row.select('input[id]')[0]['id'] ),
                'key': str( row.select('input[id]')[0]['id'] ),
                'title': row.select('.patFuncTitle')[0].get_text(strip=True),
                'status': row.select('.patFuncStatus')[0].get_text(strip=True),
                'pickup': row.select('.patFuncPickup')[0].get_text(strip=True),
                'cancel_by': row.select('.patFuncCancel')[0].get_text(strip=True), } )
        return holds

    def get_items(self, bib):
        """
        Get the item numbers linked to a bib record.  If no item number is
        returned, this item isn't requestable.
        """
        url = self.request_base.replace('{{bib}}', bib)
        payload = {
            'name' : self.name,
            'code' : self.barcode,
            'pat_submit':'xxx',
            'neededby_Month': '2',
            'neededby_Day': '1',
            'neededby_Year': '2011',
            'submit': 'SUBMIT',
            'loc': 'ROCK',
            #inum is optional
        }
        r = requests.post(url,
                          data=payload,
                          cookies=self.cookies)
        doc = BeautifulSoup( r.content.decode('utf-8', 'replace') )
        rows = doc.find_all( 'tr', class_='bibItemsEntry' )
        out = []
        for r in rows:
            _k = {}
            cells = r.select( 'td' )
            try:
                # item_num = unicode( cells[0].select('input[type="radio"]')[0]['value'] )
                item_num = str( cells[0].select('input[type="radio"]')[0]['value'] )
            except IndexError:
                item_num = None
            item, loc, call, status, barcode = tuple([c.get_text(strip=True) for c in cells])
            _k['id'] = item_num
            _k['location'] = loc
            _k['callnumber'] = call
            _k['status'] = status
            _k['barcode'] = barcode.replace( ' ', '' )
            out.append(_k)
        return out

    def place_hold( self, bib, item, pickup_location='ROCK', availability_location=None ):
        """ Place actual hold given bib and item. """
        out = {}
        out['bib'] = bib
        out['item'] = item
        url = self.request_base.replace('{{bib}}', bib)
        # payload = self.prep_hold_payload( bib, item, pickup_location, availability_location )
        payload = self.prep_hold_payload( bib, item, pickup_location )
        #post it
        rsp = self.session.post(url, data=payload)
        # log.debug( 'rsp.content, ```%s```' % rsp.content.decode('utf-8') )
        #Check for success message
        confirm_status = self._parse_hold_confirmation(rsp.content)
        out.update(confirm_status)
        return out

    def prep_hold_payload( self, bib, item, pickup_location ):
        """ Returns appropriate payload dct. """
        payload = {
            'code': self.barcode,
            'locx00': pickup_location,  # was 'r0001'
            'name': self.name,
            'pat_submit': 'Request item',
            'radio': item,
            'submit': 'Submit',
            }
        log.debug( 'hold payload, `%s`' % pprint.pformat(payload) )
        return payload

    # def prep_hold_payload( self, bib, item, pickup_location, availability_location ):
    #     """ Returns appropriate payload dct. """
    #     log.debug( 'availability_location, `%s`' % availability_location )
    #     if availability_location and availability_location.lower() == 'annex':
    #         payload = {
    #             'code': self.barcode,
    #             'locx00': pickup_location,  # was 'r0001'
    #             'name': self.name,
    #             'pat_submit': 'Request item',
    #             'radio': item,
    #             'submit': 'Submit',
    #             }
    #     else:
    #         payload = {
    #             'code' : self.barcode,
    #             'loc': pickup_location,
    #             'name' : self.name,
    #             'neededby_Day': 30,
    #             'neededby_Month': 12,
    #             'neededby_Year': 2015,
    #             'pat_submit':'xxx',
    #             'radio': item,
    #             'submit': 'SUBMIT',
    #             }
    #     log.debug( 'hold payload, `%s`' % pprint.pformat(payload) )
    #     return payload

    def _parse_hold_confirmation(self, content):
        """
        Helper for parsing confirmation screen.
        """
        # content = content if ( type(content) == unicode ) else content.decode( 'utf-8', 'replace' )
        content = content if ( type(content) == str ) else content.decode( 'utf-8', 'replace' )
        out = {
            'confirmed': False,
            'message': None }
        doc = BeautifulSoup( content )
        try:
            # msg = unicode( doc.find_all( 'span', class_='style1' )[0] )
            msg = str( doc.find_all( 'span', class_='style1' )[0] )
        except IndexError:
            #These are failures.
            msg = doc.find( 'font', attrs={'color': 'red', 'size': '+2'} ).get_text( strip=True )
            out['message'] = msg
            return out
        try:
            msg.index('was successful')
            out['confirmed'] = True
            return out
        except ValueError:
            return out

    def cancel_hold(self, cancel_key, seconds_to_wait=10):
        """
        The III database doesn't seem to cancel the hold in real time.

        We will try to cancel and verify the hold.  If not verified, we
        will try again, first pausing for a second.  We will try verify up to
        `seconds_to_wait`.  In testing, waiting up to 10 seconds was possible.
        """
        out = {}
        out['cancelled'] = False
        out['key'] = cancel_key
        out['patron_id'] = self.patron_id

        loc_key = cancel_key.replace('cancel', 'loc')
        payload = {
                   'currentsortorder':'current_pickup',
                   'currentsortorder':'current_pickup',
                   'updateholdssome': 'YES',
                   cancel_key: 'on',
                   loc_key: ''
        }
        url = self.opac_url + 'patroninfo~S7/%s/holds' % self.patron_id
        r = self.session.post(url, data=payload)
        elapsed = 0
        while True:
            # log.debug("Attempting to verify canceled hold.")
            #Get all the holds and verify that this key isn't in the current hold set.
            current_holds = [h['key'] for h in self.get_holds()]
            #These are failures.
            if cancel_key in current_holds:
                # Wait a second
                # log.debug("Waiting for one second.")
                time.sleep(1)
                elapsed += 1
                pass
            # Success
            else:
                break
            #Make sure we haven't passed to max seconds.
            if elapsed >= seconds_to_wait:
                raise Exception("Couldn't cancel hold in time specified.")
                break

        out['cancelled'] = True
        return out

    def cancel_all_holds(self):
        """
        Cancel all of a patron's holds.
        TODO: write test and re-implement.
        Initial implementation at <https://github.com/Brown-University-Library/josiah-patron-accounts/blob/6ca4280ec46c7a91584ca7e994faeb9dd1c87203/iii_account/iii_account.py>
        """
        pass

    def get_checkouts(self):
        """
        Get a list of items a user has checked out.
        """
        url = self.opac_url + 'patroninfo/%s/items' % self.patron_id

        rsp = self.session.get(url)
        content = rsp.content
        #Will raise if session expired message is found.
        self._validate_session(content)
        check_outs = self._parse_checkouts(content)
        return check_outs

    def _parse_checkouts(self, content):
        """
        Parse a given user's current checkouts.
        """
        # content = content if type(content) == unicode else content.decode( 'utf-8', 'replace' )
        content = content if type(content) == str else content.decode( 'utf-8', 'replace' )
        doc = BeautifulSoup( content )
        t_rows = doc.find_all( 'tr', class_='patFuncEntry' )
        def _get(chunk, selector):
            """
            little util to get text by css selector.
            """
            return chunk.select('td.%s' % selector)[0].get_text(strip=True)
        checkouts = [
            {
                # 'key': unicode( row.select('input[id]')[0]['id'] ),
                # 'item': unicode( row.select('input[value]')[0]['value'] ),
                'key': str( row.select('input[id]')[0]['id'] ),
                'item': str( row.select('input[value]')[0]['value'] ),
                'title': _get(row, 'patFuncTitle'),
                'barcode': _get(row, 'patFuncBarcode'),
                'status': _get(row, 'patFuncStatus'),
                'call_number': _get(row, 'patFuncCallNo'),
            }
            for row in t_rows
        ]
        return checkouts

    def renew_item(self):
        """
        post 1 - patroninfo~S7/x/items
        requestRenewSome:requestRenewSome
        currentsortorder:current_checkout
        renew0:i12445874
        currentsortorder:current_checkout

        post2 - /patroninfo~S7/x/items

        currentsortorder:current_checkout
        renew0:i12445874
        currentsortorder:current_checkout
        renewsome:YES

        parse renewed html for confirmation

        """
        pass

    def renew_all(self):
        pass

    def get_fines(self):
        """
        Parse the odd fines table.
        TODO: consider implementing via the patron-api.
        """
        pass
