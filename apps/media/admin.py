"""
Admin configuration for EventPhoto model.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventPhoto


@admin.register(EventPhoto)
class EventPhotoAdmin(ModelAdmin):
    """Admin interface for event photos."""
    
    list_display = [
        'photo_preview',
        'event_link',
        'uploaded_by_link',
        'is_cover_badge',
        'uploaded_date',
    ]
    
    list_filter = [
        'is_cover',
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'caption',
        'event__title',
        'uploaded_by__email',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at']
    
    autocomplete_fields = ['event', 'uploaded_by']

    @display(description=_('Photo'), header=True)
    def photo_preview(self, obj):
        if obj.url:
            # Use mark_safe for header columns with HTML
            # Add onerror handler for broken images
            return [
                mark_safe(
                    f'<img src="{obj.url}" '
                    f'style="width:80px;height:60px;object-fit:cover;border-radius:6px;background:#1f2937;" '
                    f'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';" />'
                    f'<div style="display:none;width:80px;height:60px;background:#374151;border-radius:6px;'
                    f'align-items:center;justify-content:center;color:#9ca3af;font-size:11px;">No Image</div>'
                )
            ]
        return [
            mark_safe(
                '<div style="width:80px;height:60px;background:#374151;border-radius:6px;'
                'display:flex;align-items:center;justify-content:center;color:#9ca3af;font-size:11px;">No URL</div>'
            )
        ]

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.event.pk,
            obj.event.title
        )

    @display(description=_('Uploaded By'), ordering='uploaded_by__email')
    def uploaded_by_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.uploaded_by.pk,
            obj.uploaded_by.name or obj.uploaded_by.email
        )

    @display(description=_('Cover'), ordering='is_cover')
    def is_cover_badge(self, obj):
        if obj.is_cover:
            return format_html('<span style="color:#f59e0b;font-weight:600;">★ Cover</span>')
        return '-'

    @display(description=_('Uploaded'), ordering='created_at')
    def uploaded_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')