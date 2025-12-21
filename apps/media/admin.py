from typing import List
from django.contrib.admin import register
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventPhoto

THUMB_WIDTH_PX = 80
THUMB_HEIGHT_PX = 60
THUMB_BG = '#1f2937'
NO_IMAGE_BG = '#374151'
MUTED_COLOR = '#9ca3af'
THUMB_BORDER_RADIUS = '6px'
FONT_SIZE = '11px'
IMG_STYLE_TEMPLATE = 'width:{}px;height:{}px;object-fit:cover;border-radius:{};background:{};'
NO_IMAGE_DIV_STYLE = 'display:none;width:{}px;height:{}px;background:{};border-radius:{};align-items:center;justify-content:center;color:{};font-size:{};'
NO_URL_DIV_STYLE = 'width:{}px;height:{}px;background:{};border-radius:{};display:flex;align-items:center;justify-content:center;color:{};font-size:{};'
LINK_COLOR = '#8b5cf6'
COVER_COLOR = '#f59e0b'
COVER_LABEL = '★ Cover'
NO_IMAGE_LABEL = 'No Image'
NO_URL_LABEL = 'No URL'
DATE_FORMAT = '%b %d, %Y'

@register(EventPhoto)
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
    def photo_preview(self, obj: EventPhoto) -> List[str]:
        """Return an HTML thumbnail preview for the photo or a placeholder when absent."""
        img_style = IMG_STYLE_TEMPLATE.format(THUMB_WIDTH_PX, THUMB_HEIGHT_PX, THUMB_BORDER_RADIUS, THUMB_BG)
        no_image_html_style = NO_IMAGE_DIV_STYLE.format(THUMB_WIDTH_PX, THUMB_HEIGHT_PX, NO_IMAGE_BG, THUMB_BORDER_RADIUS, MUTED_COLOR, FONT_SIZE)
        no_url_html_style = NO_URL_DIV_STYLE.format(THUMB_WIDTH_PX, THUMB_HEIGHT_PX, NO_IMAGE_BG, THUMB_BORDER_RADIUS, MUTED_COLOR, FONT_SIZE)

        if obj.url:
            html = (
                f'<img src="{obj.url}" style="{img_style}" '
                f'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';" />'
                f'<div style="{no_image_html_style}">{NO_IMAGE_LABEL}</div>'
            )
            return [mark_safe(html)]

        placeholder = f'<div style="{no_url_html_style}">{NO_URL_LABEL}</div>'
        return [mark_safe(placeholder)]

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj: EventPhoto) -> str:
        """Return an admin link to the related event."""
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:{};">{}</a>',
            obj.event.pk,
            LINK_COLOR,
            obj.event.title
        )

    @display(description=_('Uploaded By'), ordering='uploaded_by__email')
    def uploaded_by_link(self, obj: EventPhoto) -> str:
        """Return an admin link to the uploading user."""
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:{}">{}</a>',
            obj.uploaded_by.pk,
            LINK_COLOR,
            obj.uploaded_by.name or obj.uploaded_by.email
        )

    @display(description=_('Cover'), ordering='is_cover')
    def is_cover_badge(self, obj: EventPhoto) -> str:
        """Return a badge indicating if the photo is a cover photo."""
        if obj.is_cover:
            return format_html('<span style="color:{};font-weight:600;">{}</span>', COVER_COLOR, COVER_LABEL)
        return '-'

    @display(description=_('Uploaded'), ordering='created_at')
    def uploaded_date(self, obj: EventPhoto) -> str:
        """Return the formatted upload date for display in the admin."""
        return obj.created_at.strftime(DATE_FORMAT)