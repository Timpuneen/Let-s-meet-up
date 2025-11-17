from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import Event
from .serializers import EventSerializer, EventCreateSerializer, EventListSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Events'],
        summary='List all upcoming events',
        description='Returns a paginated list of all upcoming events.',
    ),
    retrieve=extend_schema(
        tags=['Events'],
        summary='Get event details',
        description='Returns detailed information about a specific event.',
    ),
    create=extend_schema(
        tags=['Events'],
        summary='Create new event',
        description='Create a new event. The authenticated user will be set as the organizer.',
        request=EventCreateSerializer,
    ),
    update=extend_schema(
        tags=['Events'],
        summary='Update event',
        description='Update all fields of an event. Only the organizer can update the event.',
    ),
    partial_update=extend_schema(
        tags=['Events'],
        summary='Partially update event',
        description='Update specific fields of an event. Only the organizer can update the event.',
    ),
    destroy=extend_schema(
        tags=['Events'],
        summary='Delete event',
        description='Delete an event. Only the organizer can delete the event.',
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for events with registration functionality.
    
    Provides endpoints for listing, creating, updating, and deleting events,
    as well as custom actions for event registration management.
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
    
    @extend_schema(
        tags=['Events'],
        summary='Register for event',
        description='Register the authenticated user as a participant for the specified event.',
        responses={
            200: OpenApiResponse(response=EventSerializer, description='Successfully registered'),
            400: OpenApiResponse(description='Cannot register (already registered or own event)'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """
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
    
    @extend_schema(
        tags=['Events'],
        summary='Cancel event registration',
        description='Remove the authenticated user from the list of participants for the specified event.',
        responses={
            200: OpenApiResponse(response=EventSerializer, description='Successfully cancelled registration'),
            400: OpenApiResponse(description='Not registered for this event'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_registration(self, request, pk=None):
        """
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
    
    @extend_schema(
        tags=['Events'],
        summary='Get my organized events',
        description='Returns a list of all events organized by the authenticated user.',
        responses={
            200: OpenApiResponse(response=EventListSerializer(many=True), description='List of organized events'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_organized(self, request):
        """
        List of events organized by current user
        """
        events = Event.objects.filter(organizer=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Events'],
        summary='Get my registered events',
        description='Returns a list of all events the authenticated user is registered for as a participant.',
        responses={
            200: OpenApiResponse(response=EventListSerializer(many=True), description='List of registered events'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_registered(self, request):
        """
        List of events the current user is registered for
        """
        events = Event.objects.filter(participants=request.user).select_related('organizer').prefetch_related('participants')
        serializer = EventListSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
