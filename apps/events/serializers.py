from django.utils import timezone

from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from apps.users.serializers import UserSerializer

from .models import Event


class EventSerializer(ModelSerializer):
    """Serializer for Event model.
    
    Provides full representation of an event including organizer details,
    participants, participant count, and registration status.
    """

    organizer = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participants_count = SerializerMethodField()
    is_registered = SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location', 
            'organizer', 'participants', 'participants_count',
            'is_registered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Return the number of participants for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            int: Number of participants.
        """
        return obj.participants.count()

    def get_is_registered(self, obj):
        """Check if the current user is registered for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            bool: True if user is registered, False otherwise.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False


class EventCreateSerializer(ModelSerializer):
    """Serializer for creating new events.
    
    Validates that the event date is in the future before creation.
    """

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']

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


class EventListSerializer(ModelSerializer):
    """Simplified serializer for event list views.
    
    Provides essential event information without full details
    for performance optimization in list views.
    """

    organizer = UserSerializer(read_only=True)
    participants_count = SerializerMethodField()
    is_registered = SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'organizer', 'participants_count', 'is_registered'
        ]

    def get_participants_count(self, obj):
        """Return the number of participants for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            int: Number of participants.
        """
        return obj.participants.count()

    def get_is_registered(self, obj):
        """Check if the current user is registered for the event.
        
        Args:
            obj: Event instance.
            
        Returns:
            bool: True if user is registered, False otherwise.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False
