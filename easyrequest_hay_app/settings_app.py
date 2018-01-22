# -*- coding: utf-8 -*-

import json, os


README_URL = os.environ[ 'EZRQST_HAY__README_URL' ]

TEST_SHIB_JSON = os.environ.get( 'EZRQST_HAY__TEST_SHIB_JSON', '' )
SHIB_ERESOURCE_PERMISSION = os.environ['EZRQST_HAY__SHIB_ERESOURCE_PERMISSION']
