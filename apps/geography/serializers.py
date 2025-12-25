from typing import Any, Dict

from rest_framework.serializers import ModelSerializer

from .models import City, Country


class CountrySerializer(ModelSerializer):
    """
    Serializer for Country model.
    
    Provides country information with id, name, and code.
    Used as a nested serializer in Event and City serializers.
    """
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']
        read_only_fields = ['id']


class CitySerializer(ModelSerializer):
    """
    Serializer for City model.
    
    Provides city information with nested country data.
    Used as a nested serializer in Event serializer.
    """
    
    country = CountrySerializer(read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'country']
        read_only_fields = ['id']
