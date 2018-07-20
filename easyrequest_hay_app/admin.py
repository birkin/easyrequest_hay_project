# -*- coding: utf-8 -*-

from django.contrib import admin
from easyrequest_hay_app.models import ItemRequest


class ItemRequestAdmin( admin.ModelAdmin ):
    date_hierarchy = 'create_datetime'
    ordering = [ '-id' ]
    list_display = [
        'id', 'create_datetime', 'item_title', 'status', 'admin_notes' ]
    list_filter = [ 'status' ]
    search_fields = [
        'id', 'create_datetime', 'status', 'item_title', 'admin_notes', 'source_url', 'full_url_params', 'patron_info' ]
    readonly_fields = [
        'id', 'create_datetime', 'modified_datetime', 'status', 'item_title', 'source_url', 'full_url_params', 'patron_info', 'short_url_segment', ]

    fieldsets = (
        ('For Sierra and Aeon', {
            'classes': ('wide',),
            'fields': (
                'item_title', 'full_url_params', 'patron_info',
            )
        }),
        ('Other', {
            'classes': ('wide',),
            'fields': (
                'source_url', 'create_datetime', 'modified_datetime', 'status', 'admin_notes', 'short_url_segment',
            ),
        }),
    )


admin.site.register( ItemRequest, ItemRequestAdmin )
