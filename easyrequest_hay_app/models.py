# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
# from django.conf import settings as project_settings
# from django.core.urlresolvers import reverse
from django.db import models
# from django.http import HttpResponseRedirect

log = logging.getLogger(__name__)


class ItemRequest( models.Model ):
    """ Contains user & item data.
        Called by Processor(). """
    item_title = models.CharField( max_length=200, blank=True, null=True, help_text="used by Millennium & Aeon" )
    status = models.CharField( max_length=200, blank=True, null=True )
    item_author = models.CharField( max_length=200, blank=True, null=True, help_text="used by Aeon" )
    item_bib = models.CharField( max_length=50, blank=True, null=True, help_text="used by Millennium & Aeon" )
    item_id = models.CharField( max_length=50, blank=True, null=True, help_text="used by Millennium" )
    item_barcode = models.CharField( max_length=50, blank=True, null=True, help_text="used by Millennium" )
    item_callnumber = models.CharField( max_length=200, blank=True, null=True, help_text="used by Millennium & Aeon" )
    item_publish_info = models.CharField( max_length=200, blank=True, null=True, help_text="used by Aeon" )
    item_digital_version_url = models.CharField( max_length=200, blank=True, null=True, help_text="used by Aeon" )
    patron_name = models.CharField( max_length=100, blank=True, null=True, help_text="used by Millennium" )  # patron full name
    patron_barcode = models.CharField( max_length=50, blank=True, null=True, help_text="used by Millennium" )
    patron_email = models.CharField( max_length=100, blank=True, null=True, help_text="used by Millennium" )
    source_url = models.TextField( blank=True, null=True )
    create_datetime = models.DateTimeField( auto_now_add=True, blank=True, null=True )  # blank=True for backward compatibility
    admin_notes = models.TextField( blank=True, null=True )
    full_url_params = models.TextField( blank=True, null=True )
    short_url_segment = models.CharField( max_length=20, blank=True, null=True )

    def __unicode__(self):
        return smart_text( 'id: %s || title: %s' % (self.id, self.item_title) , 'utf-8', 'replace' )

    def jsonify(self):
        """ Returns object data in json-compatible dict. """
        jsn = serializers.serialize( 'json', [self] )  # json string is single-item list
        lst = json.loads( jsn )
        object_dct = lst[0]
        return ItemRequest

    # end class ItemRequest
