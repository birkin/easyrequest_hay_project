# -*- coding: utf-8 -*-

import json, logging, os, pprint
from django.conf import settings as project_settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from easyrequest_hay_app import settings_app
from easyrequest_hay_app.lib.patron_api import PatronApiHelper
from easyrequest_hay_app.models import ItemRequest



log = logging.getLogger(__name__)

papi_helper = PatronApiHelper()


class ShibViewHelper( object ):
    """ Contains helpers for views.shib_login()
        Called by views.shib_login() """

    def check_shib_headers( self, request ):
        """ Grabs and checks shib headers, returns boolean.
            Called by views.shib_login() """
        shib_checker = ShibChecker()
        shib_dict = shib_checker.grab_shib_info( request )
        validity = shib_checker.evaluate_shib_info( shib_dict )
        log.debug( 'returning shib validity `%s`' % validity )
        return ( validity, shib_dict )

    def prep_login_redirect( self, request ):
        """ Prepares redirect response-object to views.login() on bad authZ (p-type problem).
            Called by views.shib_login() """
        request.session['shib_login_error'] = 'Problem on authorization.'
        request.session['shib_authorized'] = False
        redirect_url = '%s?bibnum=%s&barcode=%s' % ( reverse('login_url'), request.session['item_bib'], request.session['item_barcode'] )
        log.debug( 'ShibViewHelper redirect_url, `%s`' % redirect_url )
        resp = HttpResponseRedirect( redirect_url )
        return resp

    def build_processor_response( self, shortlink, shib_dict ):
        """ Saves user info & redirects to behind-the-scenes processor page.
            Called by views.shib_login() """
        log.debug( 'starting build_response()' )
        log.debug( 'shortlink, `%s`' % shortlink )
        log.debug( 'shib_dict, ```%s```' % shib_dict )
        item_request = ItemRequest.objects.get( short_url_segment=shortlink )
        item_request.patron_info = json.dumps( shib_dict, sort_keys=True, indent=2 )
        item_request.save()
        redirect_url = '%s?shortlink=%s' % ( reverse('processor_url'), shortlink )
        log.debug( 'leaving ShibViewHelper; redirect_url `%s`' % redirect_url )
        return = HttpResponseRedirect( redirect_url )

    ## end class ShibViewHelper


class ShibChecker( object ):
    """ Contains helpers for checking Shib.
        Called by ShibViewHelper() """

    def __init__( self ):
        self.TEST_SHIB_JSON = settings_app.TEST_SHIB_JSON
        self.SHIB_ERESOURCE_PERMISSION = settings_app.SHIB_ERESOURCE_PERMISSION

    def grab_shib_info( self, request ):
        """ Grabs shib values from http-header or dev-settings.
            Called by models.ShibViewHelper.check_shib_headers() """
        log.debug( 'self.TEST_SHIB_JSON, ```%s```' % self.TEST_SHIB_JSON )
        log.debug( 'request.get_host(), ```%s```' % request.get_host() )
        shib_dict = {}
        # if 'Shibboleth-eppn' in request.META:
        if 'HTTP_SHIBBOLETH_EPPN' in request.META:
            shib_dict = self.grab_shib_from_meta( request )
        else:
            if '127.0.0.1' in request.get_host() and project_settings.DEBUG == True:
                shib_dict = json.loads( self.TEST_SHIB_JSON )
        log.debug( 'shib_dict is: %s' % pprint.pformat(shib_dict) )
        return shib_dict

    def grab_shib_from_meta( self, request ):
        """ Extracts shib values from http-header.
            Called by grab_shib_info() """
        shib_dict = {
            'eppn': request.META.get( 'HTTP_SHIBBOLETH_EPPN', '' ),
            'firstname': request.META.get( 'HTTP_SHIBBOLETH_GIVENNAME', '' ),
            'lastname': request.META.get( 'HTTP_SHIBBOLETH_SN', '' ),
            'email': request.META.get( 'HTTP_SHIBBOLETH_MAIL', '' ).lower(),
            'patron_barcode': request.META.get( 'HTTP_SHIBBOLETH_BROWNBARCODE', '' ),
            'member_of': request.META.get( 'HTTP_SHIBBOLETH_ISMEMBEROF', '' ) }
        return shib_dict

    def evaluate_shib_info( self, shib_dict ):
        """ Returns boolean.
            Called by ShibViewHelper.check_shib_headers() """
        validity = False
        if self.all_values_present(shib_dict):
            if self.brown_user_confirmed(shib_dict):
                if self.authorized( shib_dict['patron_barcode'] ):
                    validity = True
        log.debug( 'validity, `%s`' % validity )
        return validity

    def all_values_present( self, shib_dict ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        present_check = False
        if sorted( shib_dict.keys() ) == ['email', 'eppn', 'firstname', 'lastname', 'member_of', 'patron_barcode']:
            value_test = 'init'
            for (key, value) in shib_dict.items():
                if len( value.strip() ) == 0:
                    value_test = 'fail'
            if value_test == 'init':
                present_check = True
        log.debug( 'present_check, `%s`' % present_check )
        return present_check

    def brown_user_confirmed( self, shib_dict ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        brown_check = False
        if '@brown.edu' in shib_dict['eppn']:
            brown_check = True
        log.debug( 'brown_check, `%s`' % brown_check )
        return brown_check

    def authorized( self, patron_barcode ):
        """ Returns boolean.
            Called by evaluate_shib_info() """
        authZ_check = False
        papi_helper.process_barcode( patron_barcode )
        if papi_helper.ptype_validity is True:
            authZ_check = True
        log.debug( 'authZ_check, `%s`' % authZ_check )
        return authZ_check

    ## end class ShibChecker
