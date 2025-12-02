"""
Admin configuration for Country and City models.
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter

from .models import Country, City


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    """Admin interface for countries."""
    
    list_display = [
        'name_with_flag',
        'code',
        'cities_count',
        'events_count',
    ]
    
    search_fields = ['name', 'code']
    
    ordering = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            cities_total=Count('cities', distinct=True),
            events_total=Count('events', distinct=True),
        )

    @display(description=_('Country'), ordering='name', header=True)
    def name_with_flag(self, obj):
        # Use mark_safe for header columns
        return [mark_safe(
            f'<span style="font-size:18px;margin-right:8px;">{self.get_flag_emoji(obj.code)}</span>'
            f'<strong>{obj.name}</strong>'
        )]

    @display(description=_('Cities'), ordering='cities_total')
    def cities_count(self, obj):
        return format_html(
            '<span style="color:#8b5cf6;font-weight:500;">{}</span>',
            obj.cities_total
        )

    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj):
        count = obj.events_total
        if count > 0:
            return format_html(
                '<a href="/admin/events/event/?country__id__exact={}" style="color:#8b5cf6;">{} events</a>',
                obj.pk,
                count
            )
        return '0'

    @staticmethod
    def get_flag_emoji(code):
        """Convert country code to flag emoji."""
        if not code or len(code) != 2:
            return '🏴'
        return ''.join(chr(127397 + ord(c)) for c in code.upper())


@admin.register(City)
class CityAdmin(ModelAdmin):
    """Admin interface for cities."""
    
    list_display = [
        'city_name',
        'country_link',
        'events_count',
    ]
    
    list_filter = [
        ('country', RelatedDropdownFilter),
    ]
    
    search_fields = ['name', 'country__name']
    
    ordering = ['name']
    
    autocomplete_fields = ['country']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('country').annotate(
            events_total=Count('events')
        )

    @display(description=_('City'), ordering='name', header=True)
    def city_name(self, obj):
        # Use mark_safe for header columns
        return [mark_safe(f'<strong>{obj.name}</strong>')]

    @display(description=_('Country'), ordering='country__name')
    def country_link(self, obj):
        return format_html(
            '<a href="/admin/geography/country/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.country.pk,
            obj.country.name
        )

    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj):
        count = obj.events_total
        if count > 0:
            return format_html(
                '<a href="/admin/events/event/?city__id__exact={}" style="color:#8b5cf6;">{} events</a>',
                obj.pk,
                count
            )
        return '0'