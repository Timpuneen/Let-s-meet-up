from typing import List

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RelatedDropdownFilter
from unfold.decorators import display

from .models import City, Country


COUNTRY_CODE_LENGTH = 2
FLAG_EMOJI_BASE = 127397
DEFAULT_FLAG_EMOJI = '🏴'
ZERO_COUNT = '0'

ADMIN_URL_COUNTRY_CHANGE = '/admin/geography/country/{}/change/'
ADMIN_URL_EVENTS_BY_COUNTRY = '/admin/events/event/?country__id__exact={}'
ADMIN_URL_EVENTS_BY_CITY = '/admin/events/event/?city__id__exact={}'

COLOR_PRIMARY = '#8b5cf6'

HTML_STYLE_FLAG = 'font-size:18px;margin-right:8px;'
HTML_STYLE_COLOR_PRIMARY = f'color:{COLOR_PRIMARY};font-weight:500;'
HTML_STYLE_LINK_PRIMARY = f'color:{COLOR_PRIMARY};'


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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Country]:
        """
        Get queryset with annotated counts.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            QuerySet: Annotated queryset with cities and events counts.
        """
        qs = super().get_queryset(request)
        return qs.annotate(
            cities_total=Count('cities', distinct=True),
            events_total=Count('events', distinct=True),
        )

    @display(description=_('Country'), ordering='name', header=True)
    def name_with_flag(self, obj: Country) -> List[SafeString]:
        """
        Display country name with flag emoji.
        
        Args:
            obj: Country instance.
            
        Returns:
            List[SafeString]: HTML formatted country name with flag.
        """
        return [mark_safe(
            f'<span style="{HTML_STYLE_FLAG}">{self.get_flag_emoji(obj.code)}</span>'
            f'<strong>{obj.name}</strong>'
        )]

    @display(description=_('Cities'), ordering='cities_total')
    def cities_count(self, obj: Country) -> SafeString:
        """
        Display cities count.
        
        Args:
            obj: Country instance.
            
        Returns:
            SafeString: HTML formatted cities count.
        """
        return format_html(
            '<span style="{}">{}</span>',
            HTML_STYLE_COLOR_PRIMARY,
            obj.cities_total
        )

    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj: Country) -> SafeString:
        """
        Display events count with link to filtered events.
        
        Args:
            obj: Country instance.
            
        Returns:
            SafeString: HTML formatted events count with link or zero.
        """
        count = obj.events_total
        if count > 0:
            return format_html(
                '<a href="{}" style="{}">{} events</a>',
                ADMIN_URL_EVENTS_BY_COUNTRY.format(obj.pk),
                HTML_STYLE_LINK_PRIMARY,
                count
            )
        return ZERO_COUNT

    @staticmethod
    def get_flag_emoji(code: str) -> str:
        """
        Convert country code to flag emoji.
        
        Args:
            code: Two-letter country code.
            
        Returns:
            str: Flag emoji or default flag if invalid code.
        """
        if not code or len(code) != COUNTRY_CODE_LENGTH:
            return DEFAULT_FLAG_EMOJI
        return ''.join(chr(FLAG_EMOJI_BASE + ord(c)) for c in code.upper())


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

    def get_queryset(self, request: HttpRequest) -> QuerySet[City]:
        """
        Get queryset with related country and annotated counts.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            QuerySet: Optimized queryset with events count.
        """
        qs = super().get_queryset(request)
        return qs.select_related('country').annotate(
            events_total=Count('events')
        )

    @display(description=_('City'), ordering='name', header=True)
    def city_name(self, obj: City) -> List[SafeString]:
        """
        Display city name in bold.
        
        Args:
            obj: City instance.
            
        Returns:
            List[SafeString]: HTML formatted city name.
        """
        return [mark_safe(f'<strong>{obj.name}</strong>')]

    @display(description=_('Country'), ordering='country__name')
    def country_link(self, obj: City) -> SafeString:
        """
        Display country name as link to country admin page.
        
        Args:
            obj: City instance.
            
        Returns:
            SafeString: HTML formatted link to country.
        """
        return format_html(
            '<a href="{}" style="{}">{}</a>',
            ADMIN_URL_COUNTRY_CHANGE.format(obj.country.pk),
            HTML_STYLE_LINK_PRIMARY,
            obj.country.name
        )

    @display(description=_('Events'), ordering='events_total')
    def events_count(self, obj: City) -> SafeString:
        """
        Display events count with link to filtered events.
        
        Args:
            obj: City instance.
            
        Returns:
            SafeString: HTML formatted events count with link or zero.
        """
        count = obj.events_total
        if count > 0:
            return format_html(
                '<a href="{}" style="{}">{} events</a>',
                ADMIN_URL_EVENTS_BY_CITY.format(obj.pk),
                HTML_STYLE_LINK_PRIMARY,
                count
            )
        return ZERO_COUNT