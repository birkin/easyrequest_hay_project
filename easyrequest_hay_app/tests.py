# -*- coding: utf-8 -*-

import logging, pprint
from django.test import TestCase
# from django.test import SimpleTestCase as TestCase    ## TestCase requires db, so if you're not using a db, and want tests, try this


log = logging.getLogger(__name__)
TestCase.maxDiff = None


class ClientTest( TestCase ):
    """ Checks urls. """

    def test_landing_page_response_A(self):
        """ Checks incomplete landing-page request. """
        response = self.client.get( '/confirm/', {} )
        # log.debug( 'client session, ```%s```' % pprint.pformat(dict(self.client.session)) )
        self.assertEqual( 400, response.status_code )  # permanent redirect
        self.assertTrue( b'easyrequest-hay problem' in response.content )
        self.assertTrue( b'If you think you should be able to use this service, but cannot, please contact' in response.content )

    def test_root_url_no_slash(self):
        """ Checks '/root_url'. """
        response = self.client.get( '' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url = response._headers['location'][1]
        self.assertEqual(  '/info/', redirect_url )

    def test_root_url_slash(self):
        """ Checks '/root_url/'. """
        response = self.client.get( '/' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url = response._headers['location'][1]
        self.assertEqual(  '/info/', redirect_url )

    # end class RootUrlTest()
