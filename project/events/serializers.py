from rest_framework import serializers
from .models import Event
from users.serializers import UserSerializer


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Event"""
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
        """Возвращает количество участников"""
        return obj.participants.count()
    
    def get_is_registered(self, obj):
        """Проверяет, зарегистрирован ли текущий пользователь на мероприятие"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False


class EventCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания мероприятия"""
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'date']
    
    def validate_date(self, value):
        """Проверяет, что дата мероприятия в будущем"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError('Дата мероприятия должна быть в будущем')
        return value


class EventListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка мероприятий"""
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
