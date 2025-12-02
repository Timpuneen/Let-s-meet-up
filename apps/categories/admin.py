from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Category, EventCategory


class EventCategoryInline(admin.TabularInline):
    """Inline for event categories."""
    model = EventCategory
    extra = 1
    autocomplete_fields = ['event']


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin interface for categories."""
    
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(events_total=Count('events'))

    @display(description=_('Category'), ordering='name', header=True)
    def name_badge(self, obj):
        return [
            format_html(
                '<span style="background:#e0e7ff;color:#4f46e5;padding:6px 14px;border-radius:8px;font-weight:500;">{}</span>',
                obj.name
            )
        ]


    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj):
        count = obj.events_total
        if count > 0:
            return format_html(
                '<a href="/admin/events/event/?categories__id__exact={}" style="color:#8b5cf6;font-weight:500;">{} events</a>',
                obj.pk,
                count
            )
        return format_html('<span style="color:#9ca3af;">0 events</span>')

    @display(description=_('Created'), ordering='created_at')
    def created_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
