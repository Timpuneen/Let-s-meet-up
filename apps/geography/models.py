from django.db.models import (
    CharField,
    ForeignKey,
    Index,
    CASCADE,
)

from apps.abstracts.models import AbstractTimestampedModel

COUNTRY_NAME_MAX_LENGTH = 100
COUNTRY_CODE_MAX_LENGTH = 2
CITY_NAME_MAX_LENGTH = 100


class Country(AbstractTimestampedModel):
    """
    Country model for storing country information.
    
    Attributes:
        name (str): Full country name.
        code (str): ISO 3166-1 alpha-2 country code (e.g., 'US', 'KZ').
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
    """
    
    name = CharField(
        max_length=COUNTRY_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Country Name',
        help_text='Full name of the country',
    )
    code = CharField(
        max_length=COUNTRY_CODE_MAX_LENGTH,
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
            Index(fields=['code']),
            Index(fields=['name']),
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
    
    name = CharField(
        max_length=CITY_NAME_MAX_LENGTH,
        verbose_name='City Name',
        help_text='Name of the city',
    )
    country = ForeignKey(
        Country,
        on_delete=CASCADE,
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
            Index(fields=['name']),
            Index(fields=['country', 'name']),
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