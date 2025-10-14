from rest_framework import serializers
from .models import Event
from users.serializers import UserSerializer


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    organizer = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 
            'organizer', 'participants', 'participants_count',
            'is_registered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Returns the number of participants"""
        return obj.participants.count()
    
    def get_is_registered(self, obj):
        """Checks if the current user is registered for the event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating event"""
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'date']
    
    def validate_date(self, value):
        """Validates that the event date is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError('Event date must be in the future')
        return value


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for event list"""
    organizer = UserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date',
            'organizer', 'participants_count', 'is_registered'
        ]
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False
