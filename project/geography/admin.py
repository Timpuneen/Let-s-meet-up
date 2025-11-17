"""Admin configuration for geography models."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Country, City


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    """
    Admin interface for Country model.
    
    Provides list display, search, and filtering capabilities
    for managing countries.
    """
    
    list_display = ['name', 'code', 'cities_count', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']
    ordering = ['name']
    readonly_fields = ['created_at']
    
    def cities_count(self, obj: Country) -> int:
        """
        Get the number of cities in this country.
        
        Args:
            obj: Country instance.
        
        Returns:
            int: Number of cities.
        """
        return obj.cities.count()
    
    cities_count.short_description = 'Cities'


@admin.register(City)
class CityAdmin(ModelAdmin):
    """
    Admin interface for City model.
    
    Provides list display, search, and filtering capabilities
    for managing cities.
    """
    
    list_display = ['name', 'country', 'created_at']
    search_fields = ['name', 'country__name', 'country__code']
    list_filter = ['country', 'created_at']
    ordering = ['country', 'name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['country']