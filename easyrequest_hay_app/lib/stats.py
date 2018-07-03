import json, logging, pprint
from django.core.urlresolvers import reverse


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
            self._handle_bad_params( scheme, host )
            return False
        else:  # valid
            self.date_start = '%s 00:00:00' % get_params['start_date']
            self.date_end = '%s 23:59:59' % get_params['end_date']
            return True

    def run_query( self ):
        """ Queries db.
            Called by views.stats_v1() """
        requests = ScanRequest.objects.filter(
            create_datetime__gte=self.date_start).filter(create_datetime__lte=self.date_end)
        return requests

    def process_results( self, requests ):
        """ Extracts desired data from resultset.
            Called by views.stats_v1() """
        data = { 'count_request_for_period': len(requests) }
        for request in requests:
            # TODO: add in 'source'
            pass
        return data

    def build_response( self, data ):
        """ Builds json response.
            Called by views.stats_v1() """
        jdict = {
            'request': {
                'date_begin': self.date_start, 'date_end': self.date_end },
            'response': {
                'count_total': data['count_request_for_period'] }
            }
        self.output = json.dumps( jdict, sort_keys=True, indent=2 )
        return

    def _handle_bad_params( self, scheme, host ):
        """ Prepares bad-parameters data.
            Called by check_params() """
        data = {
          'request': { 'url': reverse( 'stats_url' ) },
          'response': {
            'status': '400 / Bad Request',
            'message': 'example url: %s://%s%s?start_date=2018-07-01&end_date=2018-07-31' % ( scheme, host, reverse('stats_url') ),
            }
          }
        self.output = json.dumps( data, sort_keys=True, indent=2 )
        return

    # end class StatsBuilder
