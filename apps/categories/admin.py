from typing import Any

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Category, EventCategory


ADMIN_EVENT_LIST_URL: str = '/admin/events/event/?categories__id__exact={}'

CATEGORY_BADGE_STYLE: str = 'background:#e0e7ff;color:#4f46e5;padding:6px 14px;border-radius:8px;font-weight:500;'
EVENT_LINK_STYLE: str = 'color:#8b5cf6;font-weight:500;'
EMPTY_EVENT_STYLE: str = 'color:#9ca3af;'

DATE_FORMAT: str = '%b %d, %Y'
INLINE_EXTRA_FORMS: int = 1
ZERO_EVENTS: int = 0


class EventCategoryInline(admin.TabularInline):
    """
    Inline admin interface for event categories.
    
    Allows managing event-category relationships directly from the Category admin page.
    """
    model = EventCategory
    extra = INLINE_EXTRA_FORMS
    autocomplete_fields = ['event']


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Admin interface for categories.
    
    Provides category management with event count annotations and custom display methods.
    """
    
    list_display = [
        'name_badge',
        'slug',
        'events_count',
        'created_date',
    ]
    
    search_fields = ['name', 'slug']
    
    ordering = ['name']
    
    readonly_fields = ['created_at']
    
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = [EventCategoryInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Get the queryset for the admin list view.
        
        Annotates queryset with the count of related events for efficient display.
        
        Args:
            request: The HTTP request object.
        
        Returns:
            QuerySet: Annotated queryset with events_total count.
        """
        qs = super().get_queryset(request)
        return qs.annotate(events_total=Count('event_categories'))

    @display(description=_('Category'), ordering='name', header=True)
    def name_badge(self, obj: Category) -> list[SafeString]:
        """
        Display category name as a styled badge.
        
        Args:
            obj: The Category instance.
        
        Returns:
            list[SafeString]: List containing the formatted HTML badge.
        """
        return [
            format_html(
                '<span style="{}">{}</span>',
                CATEGORY_BADGE_STYLE,
                obj.name
            )
        ]

    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj: Category) -> SafeString:
        """
        Display the count of events in the category.
        
        Shows a clickable link to filtered events if count > 0, otherwise shows "0 events".
        
        Args:
            obj: The Category instance with events_total annotation.
        
        Returns:
            SafeString: Formatted HTML with event count or link.
        """
        count: int = getattr(obj, 'events_total', ZERO_EVENTS)
        if count > ZERO_EVENTS:
            return format_html(
                '<a href="{}" style="{}">{} events</a>',
                ADMIN_EVENT_LIST_URL.format(obj.pk),
                EVENT_LINK_STYLE,
                count
            )
        return format_html('<span style="{}">0 events</span>', EMPTY_EVENT_STYLE)

    @display(description=_('Created'), ordering='created_at')
    def created_date(self, obj: Category) -> str:
        """
        Display the creation date in a formatted string.
        
        Args:
            obj: The Category instance.
        
        Returns:
            str: Formatted date string (e.g., "Jan 15, 2024").
        """
        return obj.created_at.strftime(DATE_FORMAT)