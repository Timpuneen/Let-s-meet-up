from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer, EventCreateSerializer, EventListSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с мероприятиями
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    def get_queryset(self):
        """Возвращает только предстоящие мероприятия для списка"""
        if self.action == 'list':
            return Event.objects.filter(date__gte=timezone.now()).select_related('organizer').prefetch_related('participants')
        return Event.objects.all().select_related('organizer').prefetch_related('participants')
    
    def perform_create(self, serializer):
        """Автоматически назначает текущего пользователя организатором"""
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """
        POST /api/events/{id}/register/
        Регистрация на мероприятие
        """
        event = self.get_object()
        user = request.user
        
        # Проверка: нельзя зарегистрироваться на свое мероприятие
        if event.organizer == user:
            return Response(
                {'error': 'Вы не можете зарегистрироваться на свое мероприятие'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка: уже зарегистрирован
        if event.participants.filter(id=user.id).exists():
            return Response(
                {'error': 'Вы уже зарегистрированы на это мероприятие'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Регистрация
        event.participants.add(user)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        """
        POST /api/events/{id}/cancel_registration/
        Отмена регистрации на мероприятие
        """
        event = self.get_object()
        user = request.user
        
        # Проверка: зарегистрирован ли пользователь
        if not event.participants.filter(id=user.id).exists():
            return Response(
                {'error': 'Вы не зарегистрированы на это мероприятие'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отмена регистрации
        event.participants.remove(user)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_organized(self, request):
        """
        GET /api/events/my_organized/
        Список мероприятий, организованных текущим пользователем
        """
        events = Event.objects.filter(organizer=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_registered(self, request):
        """
        GET /api/events/my_registered/
        Список мероприятий, на которые зарегистрирован текущий пользователь
        """
        events = Event.objects.filter(participants=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
