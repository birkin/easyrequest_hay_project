# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from django.db import models

log = logging.getLogger(__name__)


class ItemRequest( models.Model ):
    """ Contains user & item data.
        Called by Processor(). """
    item_title = models.CharField( max_length=200, blank=True, null=True, help_text="used by Sierra & Aeon" )
    status = models.CharField( max_length=200, blank=True, null=True )
    source_url = models.TextField( blank=True, null=True )
    create_datetime = models.DateTimeField( auto_now_add=True, blank=True, null=True )  # blank=True for backward compatibility
    modified_datetime = models.DateTimeField( auto_now=True, blank=True, null=True )  # blank=True for backward compatibility
    admin_notes = models.TextField( blank=True, null=True )
    patron_info = models.TextField( blank=True, null=True )  # json stored here for now
    full_url_params = models.TextField( blank=True, null=True )  # json stored here for now
    short_url_segment = models.CharField( max_length=20, blank=True, null=True )

    def __unicode__(self):
        return smart_text( 'id: %s || title: %s' % (self.id, self.item_title) , 'utf-8', 'replace' )

    def jsonify(self):
        """ Returns object data in json-compatible dict. """
        jsn = serializers.serialize( 'json', [self] )  # json string is single-item list
        lst = json.loads( jsn )
        object_dct = lst[0]
        return ItemRequest

    ## end class ItemRequest
