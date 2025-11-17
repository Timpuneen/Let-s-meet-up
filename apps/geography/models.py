"""
Geography models for countries and cities.

This module contains models for storing geographical data
used for event locations.
"""

from django.db import models

from apps.abstracts.models import AbstractTimestampedModel


class Country(AbstractTimestampedModel):
    """
    Country model for storing country information.
    
    Attributes:
        name (str): Full country name.
        code (str): ISO 3166-1 alpha-2 country code (e.g., 'US', 'KZ').
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Country Name',
        help_text='Full name of the country',
    )
    code = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='Country Code',
        help_text='ISO 3166-1 alpha-2 country code',
    )
    
    class Meta:
        db_table = 'countries'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the country.
        
        Returns:
            str: Country name.
        """
        return self.name
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the country.
        
        Returns:
            str: Detailed country information.
        """
        return f"Country(name={self.name}, code={self.code})"


class City(AbstractTimestampedModel):
    """
    City model for storing city information.
    
    Attributes:
        name (str): City name.
        country (Country): Foreign key to the country this city belongs to.
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='City Name',
        help_text='Name of the city',
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name='Country',
        help_text='Country this city belongs to',
    )
    
    class Meta:
        db_table = 'cities'
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['country', 'name']
        unique_together = [['name', 'country']]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country', 'name']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the city.
        
        Returns:
            str: City name with country.
        """
        return f"{self.name}, {self.country.name}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the city.
        
        Returns:
            str: Detailed city information.
        """
        return f"City(name={self.name}, country={self.country.code})"