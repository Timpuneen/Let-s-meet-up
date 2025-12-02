"""
Serializers for Event management.

This module contains serializers for creating, updating, and displaying events
with proper validation, optimization, and nested relationships.
"""

from django.utils import timezone

from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    PrimaryKeyRelatedField,
    ValidationError,
)

from apps.categories.serializers import CategorySerializer
from apps.users.serializers import UserSerializer
from apps.categories.models import Category

from .models import Event


class EventSerializer(ModelSerializer):
    """
    Full serializer for Event model with all details.
    
    Provides complete event information including organizer, location,
    categories, participants count, and user registration status.
    Used for retrieve operations and detailed views.
    """

    organizer = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    country_name = SerializerMethodField()
    city_name = SerializerMethodField()
    category_names = SerializerMethodField()
    participants_count = SerializerMethodField()
    is_full = SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'address','categories', 'date', 'status',
            'invitation_perm', 'max_participants', 'organizer',
            'country', 'country_name', 'city', 'city_name',
            'category_names', 'participants_count', 'is_full',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_country_name(self, obj):
        """Get country name for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            str: Country name or None.
        """
        return obj.country.name if obj.country else None
    
    def get_city_name(self, obj):
        """Get city name for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            str: City name or None.
        """
        return obj.city.name if obj.city else None
    
    def get_category_names(self, obj):
        """Get list of category names for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            list: List of category names.
        """
        return [category.name for category in obj.categories.all()]

    def get_participants_count(self, obj):
        """Return the number of accepted participants for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            int: Number of accepted participants.
        """
        return obj.get_participants_count()

    def get_is_full(self, obj):
        """Check if the event has reached maximum capacity.
        
        Args:
            obj: Event instance.
            
        Returns:
            bool: True if event is full, False otherwise.
        """
        return obj.is_full()


class EventListSerializer(ModelSerializer):
    """
    Simplified serializer for event list views.
    
    Provides essential event information for list operations
    with optimized queries (select_related/prefetch_related).
    """

    organizer = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    city_name = SerializerMethodField()
    participants_count = SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date','categories', 'address',
            'city_name', 'status', 'organizer', 'participants_count',
            'max_participants'
        ]

    
    
    def get_city_name(self, obj):
        """Get city name for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            str: City name or None.
        """
        return obj.city.name if obj.city else None

    def get_participants_count(self, obj):
        """Return the number of accepted participants for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            int: Number of accepted participants.
        """
        return obj.get_participants_count()


class EventCreateSerializer(ModelSerializer):
    """
    Serializer for creating new events.
    
    Validates event data and ensures:
    - Event date is in the future
    - City belongs to the selected country (if both provided)
    - Max participants is positive (if provided)
    """
    
    category_ids = PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text='List of category IDs to assign to the event'
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'address', 'date', 'status',
            'invitation_perm', 'max_participants', 'country', 'city',
            'category_ids'
        ]

    def validate_date(self, value):
        """Validate that the event date is in the future.
        
        Args:
            value: The date value to validate.
            
        Returns:
            datetime: The validated date.
            
        Raises:
            ValidationError: If the date is not in the future.
        """
        if value <= timezone.now():
            raise ValidationError('Event date must be in the future')
        return value
    
    def validate_max_participants(self, value):
        """Validate that max participants is positive.
        
        Args:
            value: The max_participants value to validate.
            
        Returns:
            int: The validated value.
            
        Raises:
            ValidationError: If value is not positive.
        """
        if value is not None and value < 1:
            raise ValidationError('Maximum participants must be at least 1')
        return value
    
    def validate(self, data):
        """Validate city belongs to country if both provided.
        
        Args:
            data: Dictionary containing all validated field data.
            
        Returns:
            dict: Validated data.
            
        Raises:
            ValidationError: If city doesn't belong to the selected country.
        """
        city = data.get('city')
        country = data.get('country')
        
        if city and country and city.country != country:
            raise ValidationError({
                'city': f'City {city.name} does not belong to country {country.name}'
            })
        
        return data
    
    def create(self, validated_data):
        """Create a new event with categories.
        
        Args:
            validated_data: Dictionary containing validated event data.
            
        Returns:
            Event: The newly created event instance.
        """
        category_ids = validated_data.pop('category_ids', [])
        event = Event.objects.create(**validated_data)
        
        if category_ids:
            event.categories.set(category_ids)
        
        return event


class EventUpdateSerializer(ModelSerializer):
    """
    Serializer for updating existing events.
    
    Similar to EventCreateSerializer but allows partial updates.
    Only the organizer can update their events.
    """
    
    category_ids = PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text='List of category IDs to assign to the event'
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'address', 'date', 'status',
            'invitation_perm', 'max_participants', 'country', 'city',
            'category_ids'
        ]

    def validate_date(self, value):
        """Validate that the event date is in the future.
        
        Args:
            value: The date value to validate.
            
        Returns:
            datetime: The validated date.
            
        Raises:
            ValidationError: If the date is not in the future.
        """
        if value <= timezone.now():
            raise ValidationError('Event date must be in the future')
        return value
    
    def validate_max_participants(self, value):
        """Validate that max participants is positive and not less than current count.
        
        Args:
            value: The max_participants value to validate.
            
        Returns:
            int: The validated value.
            
        Raises:
            ValidationError: If value is invalid.
        """
        if value is not None:
            if value < 1:
                raise ValidationError('Maximum participants must be at least 1')
            
            # Check current participants count
            instance = self.instance
            if instance:
                current_count = instance.get_participants_count()
                if value < current_count:
                    raise ValidationError(
                        f'Cannot set max participants to {value}. '
                        f'Event already has {current_count} participants.'
                    )
        
        return value
    
    def validate(self, data):
        """Validate city belongs to country if both provided.
        
        Args:
            data: Dictionary containing all validated field data.
            
        Returns:
            dict: Validated data.
            
        Raises:
            ValidationError: If city doesn't belong to the selected country.
        """
        city = data.get('city')
        country = data.get('country')
        
        # If only city is provided, get country from instance
        if city and not country and self.instance:
            country = self.instance.country
        
        if city and country and city.country != country:
            raise ValidationError({
                'city': f'City {city.name} does not belong to country {country.name}'
            })
        
        return data
    
    def update(self, instance, validated_data):
        """Update an event with new data including categories.
        
        Args:
            instance: Existing event instance.
            validated_data: Dictionary containing validated update data.
            
        Returns:
            Event: The updated event instance.
        """
        category_ids = validated_data.pop('category_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if category_ids is not None:
            instance.categories.set(category_ids)
        
        return instance
