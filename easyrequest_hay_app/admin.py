# -*- coding: utf-8 -*-

from django.contrib import admin
from easyrequest_hay_app.models import ItemRequest


class ItemRequestAdmin( admin.ModelAdmin ):
    date_hierarchy = 'create_datetime'
    ordering = [ '-id' ]
    list_display = [
        'id', 'create_datetime', 'modified_datetime', 'item_title', 'status', 'admin_notes' ]
    # list_filter = [ 'patron_barcode' ]
    search_fields = [
        'id', 'create_datetime', 'status', 'item_title', 'admin_notes', 'source_url' ]
    readonly_fields = [
        'id', 'create_datetime', 'modified_datetime', 'status', 'item_title', 'source_url','full_url_params', 'patron_info', 'short_url_segment', ]

    fieldsets = (
        ('For Milliennium and Aeon', {
            'classes': ('wide',),
            'fields': (
                'item_title', 'full_url_params', 'patron_info',
            )
        }),
        # ('For Aeon only', {
        #     'classes': ('wide',),
        #     'fields': (
        #         'item_author', 'item_publish_info', 'item_digital_version_url'
        #     ),
        # }),
        ('Other', {
            'classes': ('wide',),
            'fields': (
                'source_url', 'create_datetime', 'modified_datetime', 'admin_notes', 'short_url_segment',
            ),
        }),
    )


# class ItemRequestAdmin( admin.ModelAdmin ):
#     date_hierarchy = 'create_datetime'
#     ordering = [ '-id' ]
#     list_display = [
#         'id', 'create_datetime', 'status',
#         'item_title', 'item_barcode', 'item_id', 'item_bib', 'item_callnumber',
#         'patron_name', 'patron_barcode', 'patron_email',
#         'admin_notes', 'source_url' ]
#     # list_filter = [ 'patron_barcode' ]
#     search_fields = [
#         'id', 'create_datetime', 'status',
#         'item_title', 'item_barcode', 'item_id', 'item_bib', 'item_callnumber',
#         'patron_name', 'patron_barcode', 'patron_email',
#         'admin_notes', 'source_url' ]
#     readonly_fields = [
#         'id', 'create_datetime', 'status',
#         'item_title', 'item_barcode', 'item_id', 'item_bib', 'item_callnumber',
#         'patron_name', 'patron_barcode', 'patron_email',
#         'admin_notes', 'source_url' ]

#     fieldsets = (
#         ('For Milliennium and Aeon', {
#             'classes': ('wide',),
#             'fields': (
#                 'item_title', 'item_barcode', 'item_id', 'item_bib', 'item_callnumber', 'patron_name', 'patron_barcode', 'patron_email',
#             )
#         }),
#         ('For Aeon only', {
#             'classes': ('wide',),
#             'fields': (
#                 'item_author', 'item_publish_info', 'item_digital_version_url'
#             ),
#         }),
#         ('Other', {
#             'classes': ('wide',),
#             'fields': (
#                 'source_url', 'create_datetime', 'admin_notes', 'full_url_params', 'short_url_segment'
#             ),
#         }),
#     )


admin.site.register( ItemRequest, ItemRequestAdmin )
