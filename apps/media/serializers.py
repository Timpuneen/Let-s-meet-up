from typing import Any, Dict

from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError

from apps.media.models import EventPhoto
from apps.users.serializers import UserSerializer

URL_PREFIXES = ('http://', 'https://')
ERR_URL_REQUIRED = 'URL is required'
ERR_URL_SCHEME = 'URL must start with http:// or https://'
ERR_AUTH_REQUIRED = 'Authentication required'
ERR_PERMISSION = 'You must be the event organizer or a participant to upload photos'


class PhotoSerializer(ModelSerializer):
    """Serializer for EventPhoto model.
    
    Provides complete photo information including uploader details
    and cover status for read operations.
    """
    
    uploaded_by: UserSerializer = UserSerializer(read_only=True)
    
    class Meta:
        model = EventPhoto
        fields = [
            'id',
            'event',
            'uploaded_by',
            'url',
            'caption',
            'is_cover',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'is_cover', 'created_at', 'updated_at']


class PhotoListSerializer(ModelSerializer):
    """Serializer for listing EventPhoto instances.
    
    Provides a summary view of photos for list endpoints.
    """
    
    uploaded_by: UserSerializer = UserSerializer(read_only=True)
    
    class Meta:
        model = EventPhoto
        fields = [
            'id',
            'event',
            'uploaded_by',
            'url',
            'caption',
            'is_cover',
            'created_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'is_cover', 'created_at']


class PhotoCreateSerializer(ModelSerializer):
    """Serializer for creating EventPhoto instances.
    
    Handles validation and serialization for photo creation.
    The uploader is automatically set from the request context.
    """
    
    class Meta:
        model = EventPhoto
        fields = ['event', 'url', 'caption']
    
    def validate_url(self, value: str) -> str:
        """Validate that the URL is present and starts with a valid scheme."""
        if not value:
            raise ValidationError(ERR_URL_REQUIRED)

        if not value.startswith(URL_PREFIXES):
            raise ValidationError(ERR_URL_SCHEME)

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate photo data and permissions: uploader must be organizer or participant."""
        event = data.get('event')
        request = self.context.get('request')

        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            raise ValidationError(ERR_AUTH_REQUIRED)

        user = request.user

        if event.organizer == user:
            return data

        from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED

        is_participant = EventParticipant.objects.filter(
            event=event,
            user=user,
            status=PARTICIPANT_STATUS_ACCEPTED
        ).exists()

        if not is_participant:
            raise ValidationError({'event': ERR_PERMISSION})

        return data

    def create(self, validated_data: Dict[str, Any]) -> EventPhoto:
        """Create a new EventPhoto and set the uploader from the request context."""
        request = self.context.get('request')
        if request and getattr(request, 'user', None):
            validated_data['uploaded_by'] = request.user
        return EventPhoto.objects.create(**validated_data)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate photo data.
        
        Ensures that the user has permission to upload photos to the event.
        
        Args:
            data (dict): Validated field data.
        
        Returns:
            dict: Validated data.
        
        Raises:
            ValidationError: If validation fails.
        """
        event = data.get('event')
        request = self.context.get('request')
        
        if not request or not request.user:
            raise ValidationError('Authentication required')
        
        user = request.user
        
        if event.organizer == user:
            return data
        
        from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED
        
        is_participant = EventParticipant.objects.filter(
            event=event,
            user=user,
            status=PARTICIPANT_STATUS_ACCEPTED
        ).exists()
        
        if not is_participant:
            raise ValidationError({
                'event': 'You must be the event organizer or a participant to upload photos'
            })
        
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> EventPhoto:
        """
        Create a new EventPhoto instance.
        
        The uploader is automatically set from the request context.
        
        Args:
            validated_data (dict): Validated data for the new photo.
        
        Returns:
            EventPhoto: The created EventPhoto instance.
        """
        return EventPhoto.objects.create(**validated_data)


class PhotoUpdateSerializer(ModelSerializer):
    """Serializer for updating EventPhoto instances.
    
    Handles validation for photo updates.
    Only the caption and URL can be updated.
    """
    
    class Meta:
        model = EventPhoto
        fields = ['url', 'caption']
    
    def validate_url(self, value: str) -> str:
        """Validate that the URL has an allowed scheme if provided."""
        if value and not value.startswith(URL_PREFIXES):
            raise ValidationError(ERR_URL_SCHEME)

        return value
    
    def update(self, instance: EventPhoto, validated_data: Dict[str, Any]) -> EventPhoto:
        """
        Update an existing EventPhoto instance.
        
        Args:
            instance (EventPhoto): The EventPhoto instance to update.
            validated_data (dict): Validated data for the update.
        
        Returns:
            EventPhoto: The updated EventPhoto instance.
        """
        instance.url = validated_data.get('url', instance.url)
        instance.caption = validated_data.get('caption', instance.caption)
        instance.save()
        return instance

