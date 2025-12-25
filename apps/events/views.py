from typing import List, Optional

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.comments.models import EventComment
from apps.comments.serializers import CommentListSerializer
from apps.media.models import EventPhoto
from apps.media.serializers import PhotoListSerializer
from apps.participants.models import PARTICIPANT_STATUS_ACCEPTED, EventParticipant

from .models import EVENT_STATUS_PUBLISHED, Event
from .permissions import IsOrganizerOrReadOnly
from .serializers import (
    EventCreateSerializer,
    EventListSerializer,
    EventSerializer,
    EventUpdateSerializer,
)


HTTP_METHOD_PATCH = 'PATCH'


class EventViewSet(ViewSet):
    """
    ViewSet for event management operations.
    
    Provides endpoints for:
    - Listing events (with filters)
    - Creating events
    - Retrieving event details
    - Updating events (organizer only)
    - Deleting events (soft delete, organizer only)
    - Participant registration management
    - Custom filtered lists (my organized, my registered)
    """
    
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    
    def get_permissions(self) -> List[BasePermission]:
        """
        Instantiate and return the list of permissions that this view requires.
        
        Returns:
            list: Permission instances based on the action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def _get_base_queryset(self) -> QuerySet[Event]:
        """
        Get optimized base queryset with select_related and prefetch_related.
        
        Returns:
            QuerySet: Optimized event queryset.
        """
        return Event.objects.select_related(
            'organizer',
            'country',
            'city',
            'city__country'
        ).prefetch_related(
            'categories',
            Prefetch(
                'participants_rel',
                queryset=EventParticipant.objects.filter(
                    status=PARTICIPANT_STATUS_ACCEPTED
                ).select_related('user')
            )
        )
    
    @extend_schema(
        tags=['Events'],
        summary='List all published events',
        description='Returns a list of all published upcoming events with optimized queries.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=EventListSerializer(many=True),
                description='List of events. Response structure: {"count": int, "next": null, "previous": null, "results": [...]}'
            ),
        },
    )
    def list(self, request: Request) -> Response:
        """
        List all published upcoming events.
        
        Args:
            request: The request object.
        
        Returns:
            Response: List of events (200).
        """
        queryset = self._get_base_queryset().filter(
            status=EVENT_STATUS_PUBLISHED,
            date__gte=timezone.now()
        )
        serializer = EventListSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Get event details',
        description='Returns detailed information about a specific event.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=EventSerializer, description='Event details'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """
        Retrieve event details.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: Event details (200) or not found (404).
        """
        event = get_object_or_404(self._get_base_queryset(), pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Create new event',
        description='Create a new event. The authenticated user will be set as the organizer.',
        request=EventCreateSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(response=EventSerializer, description='Event created successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
        },
    )
    def create(self, request: Request) -> Response:
        """
        Create a new event.
        
        Args:
            request: The request object.
        
        Returns:
            Response: Created event data (201) or validation errors (400).
        """
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(organizer=request.user)
        
        response_serializer = EventSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def _update_event(self, request: Request, pk: int, partial: bool) -> Response:
        """
        Internal method to handle event updates.
        
        Args:
            request: The request object.
            pk: Event ID.
            partial: Whether this is a partial update (PATCH) or full update (PUT).
        
        Returns:
            Response: Updated event data (200) or errors.
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        
        self.check_object_permissions(request, event)
        
        serializer = EventUpdateSerializer(
            event, 
            data=request.data, 
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        
        response_serializer = EventSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Update event',
        description='Full update of event fields (PUT). Only the organizer can update the event.',
        request=EventUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=EventSerializer, description='Event updated successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not the organizer'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    def update(self, request: Request, pk: int) -> Response:
        """
        Full update of an event (PUT).
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: Updated event data (200) or errors.
        """
        return self._update_event(request, pk, partial=False)
    
    @extend_schema(
        tags=['Events'],
        summary='Partial update event',
        description='Partial update of event fields (PATCH). Only the organizer can update the event.',
        request=EventUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=EventSerializer, description='Event updated successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not the organizer'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        """
        Partial update of an event (PATCH).
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: Updated event data (200) or errors.
        """
        return self._update_event(request, pk, partial=True)
    
    @extend_schema(
        tags=['Events'],
        summary='Delete event (soft delete)',
        description='Soft delete an event. Only the organizer can delete the event.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description='Event deleted successfully'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not the organizer'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    def destroy(self, request: Request, pk: int) -> Response:
        """
        Soft delete an event.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: No content (204) or errors.
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        
        self.check_object_permissions(request, event)
        
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['Events'],
        summary='Register for event',
        description='Register the authenticated user as a participant for the event. '
                    'Creates a pending participation request that may need approval.',
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description='Registration successful'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Cannot register (already registered, own event, or event full)'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request: Request, pk: int) -> Response:
        """
        Register current user for the event.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: Success message (201) or error (400).
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        user = request.user
        
        if event.organizer == user:
            return Response(
                {'error': 'You cannot register for your own event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if EventParticipant.objects.filter(event=event, user=user).exists():
            return Response(
                {'error': 'You are already registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if event.is_full():
            return Response(
                {'error': 'This event has reached maximum capacity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        EventParticipant.objects.create(
            event=event,
            user=user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        return Response(
            {'message': 'Successfully registered for the event'},
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        tags=['Events'],
        summary='Cancel event registration',
        description='Remove the authenticated user from the list of participants for the event.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='Registration cancelled successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Not registered for this event'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unregister(self, request: Request, pk: int) -> Response:
        """
        Cancel registration for the event.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: Success message (200) or error (400).
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        user = request.user
        
        try:
            participation = EventParticipant.objects.get(event=event, user=user)
        except EventParticipant.DoesNotExist:
            return Response(
                {'error': 'You are not registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participation.delete()
        
        return Response(
            {'message': 'Successfully cancelled registration'},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Events'],
        summary='Get my organized events',
        description='Returns a list of all events organized by the authenticated user.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=EventListSerializer(many=True),
                description='List of organized events. Response structure: {"count": int, "next": null, "previous": null, "results": [...]}'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_organized(self, request: Request) -> Response:
        """
        List events organized by the current user.
        
        Args:
            request: The request object.
        
        Returns:
            Response: List of organized events (200).
        """
        events = self._get_base_queryset().filter(organizer=request.user)
        serializer = EventListSerializer(events, many=True)
        
        return Response({
            'count': events.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Get my registered events',
        description='Returns a list of all events the authenticated user is registered for as a participant.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=EventListSerializer(many=True),
                description='List of registered events. Response structure: {"count": int, "next": null, "previous": null, "results": [...]}'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_registered(self, request: Request) -> Response:
        """
        List events the current user is registered for.
        
        Args:
            request: The request object.
        
        Returns:
            Response: List of registered events (200).
        """
        event_ids = EventParticipant.objects.filter(
            user=request.user,
            status=PARTICIPANT_STATUS_ACCEPTED
        ).values_list('event_id', flat=True)
        
        events = self._get_base_queryset().filter(id__in=event_ids)
        serializer = EventListSerializer(events, many=True)
        
        return Response({
            'count': events.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Get all comments for event',
        description='Returns a list of all comments for a specific event, ordered by creation date.',
        parameters=[
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page (max 100)',
                required=False,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CommentListSerializer(many=True),
                description='List of comments for the event. Response structure: {"count": int, "event": int, "event_title": str, "results": [...]}'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def comments(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Get all comments for a specific event.
        
        Returns all comments associated with the event, ordered by creation date.
        Supports pagination through page_size query parameter.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: List of comments (200) or errors.
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        
        comments = EventComment.objects.filter(event=event).select_related(
            'user', 'parent'
        ).order_by('created_at')
        
        serializer = CommentListSerializer(comments, many=True)
        
        return Response({
            'count': comments.count(),
            'event': event.id,
            'event_title': event.title,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Events'],
        summary='Get all photos for event',
        description='Returns a list of all photos for a specific event, ordered by cover status and creation date.',
        parameters=[
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page (max 100)',
                required=False,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=PhotoListSerializer(many=True),
                description='List of photos for the event. Response structure: {"count": int, "event": int, "event_title": str, "results": [...]}'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found'),
        },
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def photos(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Get all photos for a specific event.
        
        Returns all photos associated with the event, ordered by cover status
        (cover photo first) then creation date.
        Supports pagination through page_size query parameter.
        
        Args:
            request: The request object.
            pk: Event ID.
        
        Returns:
            Response: List of photos (200) or errors.
        """
        event = get_object_or_404(Event.objects.all(), pk=pk)
        
        photos = EventPhoto.objects.filter(event=event).select_related(
            'uploaded_by'
        ).order_by('-is_cover', '-created_at')
        
        serializer = PhotoListSerializer(photos, many=True)
        
        return Response({
            'count': photos.count(),
            'event': event.id,
            'event_title': event.title,
            'results': serializer.data
        }, status=status.HTTP_200_OK)