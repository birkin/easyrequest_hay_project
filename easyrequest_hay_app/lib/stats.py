import datetime, json, logging, pprint
from django.core.urlresolvers import reverse
from easyrequest_hay_app.models import ItemRequest


log = logging.getLogger(__name__)


class StatsBuilder( object ):
    """ Handles stats-api calls. """

    def __init__( self ):
        self.date_start = None  # set by check_params()
        self.date_end = None  # set by check_params()
        self.output = None  # set by check_params() or...

    def check_params( self, get_params, scheme, host ):
        """ Checks parameters; returns boolean.
            Called by views.stats_v1() """
        log.debug( 'get_params, `%s`' % get_params )
        if 'start_date' not in get_params or 'end_date' not in get_params:  # not valid
            self._handle_bad_params( scheme, host, get_params )
            return False
        else:  # valid
            self.date_start = '%s 00:00:00' % get_params['start_date']
            self.date_end = '%s 23:59:59' % get_params['end_date']
            return True

    def run_query( self ):
        """ Queries db.
            Called by views.stats_api() """
        requests = ItemRequest.objects.filter(
            create_datetime__gte=self.date_start).filter(create_datetime__lte=self.date_end)
        return requests

    def process_results( self, requests ):
        """ Extracts desired data from resultset.
            Called by views.stats_v1() """
        data = {
            'count_request_for_period': len(requests),
            'disposition': {
                'initial_landing': 0, 'to_aeon_via_shib': 0, 'to_aeon_directly': 0, 'back_to_josiah': 0 }
        }
        for request in requests:
            if request.status == 'initial_landing':
                data['disposition']['initial_landing'] += 1
            elif request.status == 'to_aeon_via_shib':
                data['disposition']['to_aeon_via_shib'] += 1
            elif request.status == 'to_aeon_directly':
                data['disposition']['to_aeon_directly'] += 1
            elif request.status == 'back_to_josiah':
                data['disposition']['back_to_josiah'] += 1
            else:
                log.error( 'unhandled request.status for shortlink, `%s`; value, `%s`' % (request.short_url_segment, request.status) )
        return data

    def build_response( self, data, scheme, host, get_params ):
        """ Builds json response.
            Called by views.stats_api() """
        jdict = {
            'request': {
                'date_time': str( datetime.datetime.now() ),
                'url': '%s://%s%s%s' % ( scheme, host, reverse('stats_url'), self._prep_querystring(get_params) ),
                },
            'response': {
                'count_total': data['count_request_for_period'],
                'disposition': data['disposition'],
                'date_begin': self.date_start,
                'date_end': self.date_end,
                }
            }
        self.output = json.dumps( jdict, sort_keys=True, indent=2 )
        return

    def _handle_bad_params( self, scheme, host, get_params ):
        """ Prepares bad-parameters data.
            Called by check_params() """
        data = {
            'request': {
                'date_time': str( datetime.datetime.now() ),
                'url': '%s://%s%s%s' % ( scheme, host, reverse('stats_url'), self._prep_querystring(get_params) ) },
            'response': {
                'status': '400 / Bad Request',
                'message': 'example url: %s://%s%s?start_date=2018-07-01&end_date=2018-07-31' % ( scheme, host, reverse('stats_url') ) }
            }
        self.output = json.dumps( data, sort_keys=True, indent=2 )
        return

    def _prep_querystring( self, get_params ):
        """ Makes querystring from params.
            Called by _handle_bad_params() """
        if get_params:
            querystring = '?%s' % get_params.urlencode()  # get_params is a django QueryDict object, which has a urlencode() method! yay!
        else:
            querystring = ''
        return querystring

    # end class StatsBuilder
