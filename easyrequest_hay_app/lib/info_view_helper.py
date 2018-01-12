# -*- coding: utf-8 -*-

import datetime, logging, pprint
from easyrequest_hay_app import settings_app


log = logging.getLogger(__name__)


def build_json_context( start, scheme, host, uri_path ):
    """ Builds context that'll be converted into json by the view.
        Called by views.info() """
    context = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=scheme, hst=host, uri=uri_path ) },
        'response': {
            'documentation': settings_app.README_URL,
            'elapsed_time': str( datetime.datetime.now() - start ),
            'message': 'ok' }
    }
    log.debug( 'context, ```%s```' % pprint.pformat(context) )
    return context
