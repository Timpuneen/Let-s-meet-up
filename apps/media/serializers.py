"""
Serializers for event photo models.

This module contains serializers for the EventPhoto model,
supporting CRUD operations and photo management.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.media.models import EventPhoto
from apps.users.serializers import UserSerializer


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for EventPhoto model.
    
    Provides complete photo information including uploader details
    and cover status for read operations.
    """
    
    uploaded_by = UserSerializer(read_only=True)
    
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


class PhotoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing EventPhoto instances.
    
    Provides a summary view of photos for list endpoints.
    """
    
    uploaded_by = UserSerializer(read_only=True)
    
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


class PhotoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating EventPhoto instances.
    
    Handles validation and serialization for photo creation.
    The uploader is automatically set from the request context.
    """
    
    class Meta:
        model = EventPhoto
        fields = ['event', 'url', 'caption']
    
    def validate_url(self, value):
        """
        Validate that the URL is properly formatted.
        
        Args:
            value (str): The URL to validate.
        
        Returns:
            str: Validated URL.
        
        Raises:
            ValidationError: If URL format is invalid.
        """
        if not value:
            raise ValidationError('URL is required')
        
        # Basic URL validation
        if not (value.startswith('http://') or value.startswith('https://')):
            raise ValidationError('URL must start with http:// or https://')
        
        return value
    
    def validate(self, data):
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
        
        # Check if user is the organizer
        if event.organizer == user:
            return data
        
        # Check if user is a participant
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
    
    def create(self, validated_data):
        """
        Create a new EventPhoto instance.
        
        The uploader is automatically set from the request context.
        
        Args:
            validated_data (dict): Validated data for the new photo.
        
        Returns:
            EventPhoto: The created EventPhoto instance.
        """
        # Uploader is set in the view from request.user
        return EventPhoto.objects.create(**validated_data)


class PhotoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating EventPhoto instances.
    
    Handles validation for photo updates.
    Only the caption and URL can be updated.
    """
    
    class Meta:
        model = EventPhoto
        fields = ['url', 'caption']
    
    def validate_url(self, value):
        """
        Validate that the URL is properly formatted.
        
        Args:
            value (str): The URL to validate.
        
        Returns:
            str: Validated URL.
        
        Raises:
            ValidationError: If URL format is invalid.
        """
        if value and not (value.startswith('http://') or value.startswith('https://')):
            raise ValidationError('URL must start with http:// or https://')
        
        return value
    
    def update(self, instance, validated_data):
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

