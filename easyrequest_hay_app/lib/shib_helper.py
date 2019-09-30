""""
Contains:
- ShibLoginHelper(), which prepares a forced-authentication url for lib.confirm_helper.ConfirmHandlerHelper()
- ShibViewHelper(), called by ConfirmHandlerHelper(), which directs data-extraction and validity checks.
- ShibChecker(), called by ShibViewHelper, which actually performs the data-extraction and validity checks.
"""

import json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout as django_logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import urlquote as django_urlquote
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.lib.patron_api import PatronApiHelper
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)
papi_helper = PatronApiHelper()


class ShibLoginHelper( object ):
    """ Contains shib helpers.
        Called by lib.confirm_helper.ConfirmHandlerHelper() """

    def __init__( self ):
        self.SHIB_IDP_LOGOUT_URL = settings_app.SHIB_IDP_LOGOUT_URL

    def prep_login_url_stepA( self, request ):
        """ Preps logout url with appropriate redirect.
            Steps for login:
            - a) execute django-logout and hit idp logout url (this function)
            - b) hit sp login url w/redirect to processor-view """
        django_logout( request )
        log.debug( 'django-logout executed' )
        shortlink = request.GET['shortlink']
        log.debug( 'shortlink, `%s`' % shortlink )
        if '127.0.0.1' in request.get_host() and project_settings.DEBUG == True:
            login_a_url = '%s?shortlink=%s' % ( reverse('shib_login_url'), shortlink )
        else:
            return_url = self.prep_return_url( request )
            login_a_url = '%s?&return=%s' % ( self.SHIB_IDP_LOGOUT_URL, django_urlquote( return_url ) )
        log.debug( 'login_a_url, ```%s```' % login_a_url )
        return login_a_url

    def prep_return_url( self, request ):
        """ Preps the return url that the IDP logout url hits.
            Called by prep_login_url_stepA() """
        shortlink = request.GET['shortlink']
        return_url = '%s://%s%s?shortlink=%s' % ( request.scheme, request.get_host(), reverse('shib_login_url'), shortlink )
        log.debug( 'shib-logout-return-url, ```%s```' % return_url )
        return return_url

    ## end class ShibLoginHelper()


class ShibViewHelper( object ):
    """ Contains helpers for views.shib_login()
        Called by views.shib_login() """

    def check_shib_headers( self, request ):
        """ Grabs and checks shib headers, returns boolean.
            Called by views.shib_login_handler() """
        shib_checker = ShibChecker()
        shib_dct = shib_checker.grab_shib_info( request )
        validity = shib_checker.evaluate_shib_info( shib_dct, request )
        log.debug( 'returning shib validity `%s`' % validity )
        return ( validity, shib_dct )

    def prep_login_redirect( self, request ):
        """ Prepares redirect response-object to views.problem() on bad authZ (p-type problem).
            Called by views.shib_login_handler() """
        request.session['shib_login_error'] = 'Problem on authorization.'
        request.session['shib_authorized'] = False
        redirect_url = '%s?shortlink=%s' % ( reverse('problem_url'), request.GET['shortlink'] )
        log.debug( 'ShibViewHelper redirect_url, `%s`' % redirect_url )
        resp = HttpResponseRedirect( redirect_url )
        return resp

    def build_processor_response( self, shortlink, shib_dct ):
        """ Saves user info & redirects to behind-the-scenes processor page.
            Called by views.shib_login_handler() """
        log.debug( 'starting build_response()' )
        log.debug( 'shortlink, `%s`' % shortlink )
        log.debug( 'shib_dct, ```%s```' % shib_dct )
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        item_request.patron_info = json.dumps( shib_dct, sort_keys=True, indent=2 )
        item_request.save()
        redirect_url = '%s?shortlink=%s' % ( reverse('processor_url'), shortlink )
        log.debug( 'leaving ShibViewHelper; redirect_url `%s`' % redirect_url )
        return HttpResponseRedirect( redirect_url )

    ## end class ShibViewHelper


class ShibChecker( object ):
    """ Contains helpers for checking Shib.
        Called by ShibViewHelper() """

    def __init__( self ):
        self.TEST_SHIB_JSON = settings_app.TEST_SHIB_JSON
        self.SHIB_ERESOURCE_PERMISSION = settings_app.SHIB_ERESOURCE_PERMISSION

    def grab_shib_info( self, request ):
        """ Grabs shib values from http-header or dev-settings.
            Called by ShibViewHelper.check_shib_headers() """
        log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
        log.debug( 'self.TEST_SHIB_JSON, ```%s```' % self.TEST_SHIB_JSON )
        log.debug( 'request.get_host(), ```%s```' % request.get_host() )
        shib_dct = {}
        # if 'Shibboleth-eppn' in request.META:
        if 'HTTP_SHIBBOLETH_EPPN' in request.META:
            shib_dct = self.grab_shib_from_meta( request )
        else:
            if '127.0.0.1' in request.get_host() and project_settings.DEBUG == True:
                shib_dct = json.loads( self.TEST_SHIB_JSON )
        log.debug( 'shib_dct is: %s' % pprint.pformat(shib_dct) )
        return shib_dct

    def grab_shib_from_meta( self, request ):
        """ Extracts shib values from http-header.
            Called by grab_shib_info() """
        shib_dct = {
            'eppn': request.META.get( 'HTTP_SHIBBOLETH_EPPN', '' ),
            'firstname': request.META.get( 'HTTP_SHIBBOLETH_GIVENNAME', '' ),
            'lastname': request.META.get( 'HTTP_SHIBBOLETH_SN', '' ),
            'email': request.META.get( 'HTTP_SHIBBOLETH_MAIL', '' ).lower(),
            'patron_barcode': request.META.get( 'HTTP_SHIBBOLETH_BROWNBARCODE', '' ),
            'member_of': request.META.get( 'HTTP_SHIBBOLETH_ISMEMBEROF', '' ) }
        meta_keys = request.META.keys()
        log.debug( 'meta_keys, ```%s```' % pprint.pformat(meta_keys) )
        for demographic_category in settings_app.DEMOGRAPHIC_CATEGORIES:
            if demographic_category in meta_keys:
                shib_dct[demographic_category] = request.META[demographic_category]
        log.debug( 'shib_dct, ```%s```' % pprint.pformat(shib_dct) )
        return shib_dct

    def evaluate_shib_info( self, shib_dct, request ):
        """ Returns boolean.
            Called by ShibViewHelper.check_shib_headers() """
        validity = False
        if self.all_values_present(shib_dct):
            if self.brown_user_confirmed(shib_dct):
                if self.authorized( shib_dct['patron_barcode'], request ):
                    validity = True
        log.debug( 'validity, `%s`' % validity )
        return validity

    def all_values_present( self, shib_dct ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        ( present_check, required_keys, check_test ) = self.setup_shib_check()
        for key in required_keys:
            if self.run_shib_check( shib_dct, key ) == False:
                check_test = 'fail'
                break
        if check_test == 'init':
            present_check = True
        log.debug( 'present_check, `%s`' % present_check )
        return present_check

    def setup_shib_check( self ):
        """ Initializes and returns vars.
            Called by all_values_present() """
        present_check = False
        required_keys = ['email', 'eppn', 'firstname', 'lastname', 'member_of', 'patron_barcode']
        check_test = 'init'
        return ( present_check, required_keys, check_test )

    def run_shib_check( self, shib_dct, key ):
        """ Checks shib_dct for required key with some data.
            Called by all_values_present() """
        check_flag = False
        try:
            value = shib_dct[key]
            if len( value.strip() ) > 0:
                check_flag = True
        except:
            pass
        log.debug( 'check_flag, `%s`' % check_flag )
        return check_flag

    def brown_user_confirmed( self, shib_dct ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        brown_check = False
        if '@brown.edu' in shib_dct['eppn']:
            brown_check = True
        log.debug( 'brown_check, `%s`' % brown_check )
        return brown_check

    def authorized( self, patron_barcode, request ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        authZ_check = False
        if '127.0.0.1' in request.get_host() and project_settings.DEBUG == True:
            authZ_check = True
        else:
            # papi_helper.process_barcode( patron_barcode )
            papi_helper.process_barcode( patron_barcode, request.GET['shortlink'] )
            if papi_helper.ptype_validity is True:
                authZ_check = True
        log.debug( 'authZ_check, `%s`' % authZ_check )
        return authZ_check

    ## end class ShibChecker
