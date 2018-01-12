# # -*- coding: utf-8 -*-

# import json, logging, os, urllib
# from django.http import HttpResponseBadRequest
# from django.template import loader
# from easyrequest_hay_app.lib.pickup_location import PickupLocation


# log = logging.getLogger(__name__)
# pick_location = PickupLocation()


# class LoginViewHelper( object ):
#     """ Contains helpers for views.request_def() for handling GET. """

#     def __init__( self ):
#         """ Holds env-vars. """
#         self.AVAILABILITY_API_URL_ROOT = os.environ['EZRQST_HAY__AVAILABILITY_API_URL_ROOT']
#         self.PHONE_AUTH_HELP = os.environ['EZRQST_HAY__PHONE_AUTH_HELP']
#         self.EMAIL_AUTH_HELP = os.environ['EZRQST_HAY__EMAIL_AUTH_HELP']
#         self.LEGIT_SOURCES = json.loads( os.environ['EZRQST_HAY__LEGIT_SOURCES_JSON'] )
#         self.pic_loc_helper = PickupLocation()

#     def validate_source( self, request ):
#         """ Ensures app is accessed from legit source.
#             Called by views.login() """
#         return_val = False
#         if request.get_host() == '127.0.0.1' and project_settings.DEBUG == True:
#             return_val = True
#         referrer_host = self.get_referrer_host( request.META.get('HTTP_REFERER', 'unavailable') )
#         if referrer_host in self.LEGIT_SOURCES:
#             return_val = True
#         else:
#             log.debug( 'referrer_host, `%s`' % referrer_host )
#         log.debug( 'return_val, `%s`' % return_val )
#         return return_val

#     def get_referrer_host( self, referrer_url ):
#         """ Extracts host from referrer_url.
#             Called by validate_source() """
#         # output = urlparse.urlparse( referrer_url )
#         output = urllib.parse.urlparse( referrer_url )
#         host = output.netloc
#         log.debug( 'referrer host, `%s`' % host )
#         return host

#     def validate_params( self, request ):
#         """ Checks params.
#             Called by views.login()
#             Note: `barcode` here is the item-barcode. """
#         return_val = False
#         if sorted( request.GET.keys() ) == ['barcode', 'bibnum']:
#             if len(request.GET['bibnum']) == 8 and len(request.GET['barcode']) == 14:
#                 return_val = True
#         log.debug( 'return_val, `%s`' % return_val )
#         return return_val

#     def initialize_session( self, request ):
#         """ Initializes session.
#             Called by views.login() """
#         self._initialize_session_item_info( request )
#         self._initialize_session_user_info( request )
#         source_url = request.META.get( 'HTTP_REFERER', 'unavailable' ).strip()
#         request.session.setdefault( 'source_url', source_url )  # ensures initial valid referrer is stored, and not localhost if there's a server redirect on a login-error
#         request.session.setdefault( 'shib_login_error', False )
#         request.session['shib_authorized'] = False
#         request.session.setdefault( 'barcode_login_error', False)
#         request.session['barcode_authorized'] = False
#         log.debug( 'request.session after initialization, `%s`' % pprint.pformat(request.session.items()) )
#         return

#     def _initialize_session_item_info( self, request ):
#         """ Initializes session item info.
#             Called by initialize_session() """
#         request.session.setdefault( 'item_title', '' )
#         request.session['item_bib'] = request.GET['bibnum']
#         request.session.setdefault( 'item_id', '' )
#         request.session['item_barcode'] = request.GET['barcode']
#         request.session.setdefault( 'item_callnumber', '' )
#         request.session.setdefault( 'pickup_location', '' )
#         return

#     def _initialize_session_user_info( self, request ):
#         """ Initializes session item info.
#             Called by initialize_session() """
#         request.session['user_full_name'] = ''  # for email
#         request.session['user_last_name'] = ''  # for possible second josiah-api attempt if default shib firstname fails
#         request.session['user_email'] = ''
#         request.session.setdefault( 'barcode_login_name', '' )  # for barcode login form
#         request.session.setdefault( 'barcode_login_barcode', '21236' )  # for barcode login form
#         request.session['josiah_api_barcode'] = ''  # for josiah-patron-accounts call
#         request.session['josiah_api_name'] = ''  # for josiah-patron-accounts call
#         return

#     def get_item_info( self, bibnum, item_barcode ):
#         """ Hits availability-api for bib-title, and item id and callnumber.
#             Bib title and item callnumber are just for user display; item id needed if user proceeds.
#             Called by views.login() """
#         ( title, callnumber, item_id ) = ( '', '', '' )
#         api_dct = self.hit_availability_api( bibnum )
#         title = api_dct['response']['backend_response'][0]['title']
#         ( callnumber, item_id ) = self.process_items( api_dct, item_barcode )
#         log.debug( 'title, `%s`; callnumber, `%s`; item_id, `%s`' % (title, callnumber, item_id) )
#         return ( title, callnumber, item_id )

#     def hit_availability_api( self, bibnum ):
#         """ Returns availability-api dict.
#             Called by get_item_info() """
#         dct = {}
#         try:
#             availability_api_url = '%s/bib/%s' % ( self.AVAILABILITY_API_URL_ROOT, bibnum )
#             r = requests.get( availability_api_url )
#             dct = r.json()
#             log.debug( 'partial availability-api-response, `%s`' % pprint.pformat(dct)[0:200] )
#         except Exception as e:
#             log.error( 'exception, %s' % unicode(repr(e)) )
#         return dct

#     def process_items( self, api_dct, item_barcode ):
#         """ Extracts the callnumber and item_id from availability-api response.
#             Called by get_item_info() """
#         ( callnumber, item_id ) = ( '', '' )
#         results = api_dct['response']['backend_response']
#         for result in results:
#             items = result['items_data']
#             for item in items:
#                 if item_barcode == item['barcode']:
#                     callnumber = item['callnumber_interpreted'].replace( ' None', '' )
#                     item_id = item['item_id'][:-1]  # removes trailing check-digit
#         log.debug( 'process_items result, `%s`' % unicode(repr((callnumber, item_id))) )
#         return ( callnumber, item_id )

#     def update_session( self, request, title, callnumber, item_id ):
#         """ Updates session.
#             Called by views.login() """
#         request.session['item_title'] = title
#         request.session['item_callnumber'] = callnumber
#         request.session['item_id'] = item_id
#         log.debug( 'request.session after update, `%s`' % pprint.pformat(request.session.items()) )
#         return

#     def prepare_context( self, request ):
#         """ Prepares vars for template.
#             Called by views.login() """
#         context = {
#             'title': request.session['item_title'] ,
#             'callnumber': request.session['item_callnumber'],
#             'ROCK_code': self.pic_loc_helper.pickup_location_dct['ROCK']['code'],
#             'ROCK_display': self.pic_loc_helper.pickup_location_dct['ROCK']['display'],
#             'SCI_code': self.pic_loc_helper.pickup_location_dct['SCI']['code'],
#             'SCI_display': self.pic_loc_helper.pickup_location_dct['SCI']['display'],
#             'HAY_code': self.pic_loc_helper.pickup_location_dct['HAY']['code'],
#             'HAY_display': self.pic_loc_helper.pickup_location_dct['HAY']['display'],
#             'ORWIG_code': self.pic_loc_helper.pickup_location_dct['ORWIG']['code'],
#             'ORWIG_display': self.pic_loc_helper.pickup_location_dct['ORWIG']['display'],
#             'barcode_login_name': request.session['barcode_login_name'],
#             'barcode_login_barcode': request.session['barcode_login_barcode'],
#             'barcode_login_error': request.session['barcode_login_error'],
#             'shib_login_error': request.session['shib_login_error'],
#             'PHONE_AUTH_HELP': self.PHONE_AUTH_HELP,
#             'EMAIL_AUTH_HELP': self.EMAIL_AUTH_HELP,
#             }
#         return context

#     def prepare_badrequest_response( self, request ):
#         """ Prepares bad-request response when validation fails.
#             Called by views.login() """
#         template = loader.get_template('easyrequest_hay_app_templates/problem.html')
#         context = {
#             'help_email': self.EMAIL_AUTH_HELP,
#         }
#         bad_resp = HttpResponseBadRequest( template.render(context, request) )
#         return bad_resp


#     # end class LoginViewHelper
