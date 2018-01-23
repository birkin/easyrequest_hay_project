# -*- coding: utf-8 -*-

import json, os


README_URL = os.environ[ 'EZRQST_HAY__README_URL' ]

TEST_SHIB_JSON = os.environ.get( 'EZRQST_HAY__TEST_SHIB_JSON', '{}' )

SHIB_ERESOURCE_PERMISSION = os.environ['EZRQST_HAY__SHIB_ERESOURCE_PERMISSION']

PATRON_API_URL = os.environ['EZRQST_HAY__PAPI_URL']
PATRON_API_BASIC_AUTH_USERNAME = os.environ['EZRQST_HAY__PAPI_BASIC_AUTH_USERNAME']
PATRON_API_BASIC_AUTH_PASSWORD = os.environ['EZRQST_HAY__PAPI_BASIC_AUTH_PASSWORD']
PATRON_API_LEGIT_PTYPES = json.loads( os.environ['EZRQST_HAY__PAPI_LEGIT_PTYPES_JSON'] )

AVAILABILITY_API_URL_ROOT = os.environ['EZRQST_HAY__AVAILABILITY_API_URL_ROOT']

HAY_LOCATION_CODE = 'h0001'
