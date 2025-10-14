from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer, EventCreateSerializer, EventListSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with events
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    def get_queryset(self):
        """Returns only upcoming events for the list"""
        if self.action == 'list':
            return Event.objects.filter(date__gte=timezone.now()).select_related('organizer').prefetch_related('participants')
        return Event.objects.all().select_related('organizer').prefetch_related('participants')
    
    def perform_create(self, serializer):
        """Automatically assigns current user as organizer"""
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """
        POST /api/events/{id}/register/
        Register for event
        """
        event = self.get_object()
        user = request.user
        
        # Check: cannot register for your own event
        if event.organizer == user:
            return Response(
                {'error': 'You cannot register for your own event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check: already registered
        if event.participants.filter(id=user.id).exists():
            return Response(
                {'error': 'You are already registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registration
        event.participants.add(user)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        """
        POST /api/events/{id}/cancel_registration/
        Cancel event registration
        """
        event = self.get_object()
        user = request.user
        
        # Check: is user registered
        if not event.participants.filter(id=user.id).exists():
            return Response(
                {'error': 'You are not registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel registration
        event.participants.remove(user)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_organized(self, request):
        """
        GET /api/events/my_organized/
        List of events organized by current user
        """
        events = Event.objects.filter(organizer=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_registered(self, request):
        """
        GET /api/events/my_registered/
        List of events the current user is registered for
        """
        events = Event.objects.filter(participants=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
