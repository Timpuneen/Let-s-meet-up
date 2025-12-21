from typing import Any, Dict, Optional, Type

from django.db.models import Q, QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from .models import (
    INVITATION_STATUS_ACCEPTED,
    INVITATION_STATUS_PENDING,
    INVITATION_STATUS_REJECTED,
    EventInvitation,
)
from .permissions import IsInvitedUser, IsInvitedUserOrInviterOrReadOnly
from .serializers import (
    EventInvitationCreateSerializer,
    EventInvitationListSerializer,
    EventInvitationResponseSerializer,
    EventInvitationSerializer,
)


INVITATION_TYPE_RECEIVED = 'received'
INVITATION_TYPE_SENT = 'sent'

QUERY_PARAM_TYPE = 'type'
QUERY_PARAM_STATUS = 'status'
QUERY_PARAM_EVENT = 'event'


class EventInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing event invitations.
    
    Provides CRUD operations for invitations with filtering:
    - List: Shows invitations sent to or by the current user
    - Create: Send invitation to a user (checks permissions)
    - Retrieve: View invitation details
    - Update: Not allowed (use respond action instead)
    - Delete: Cancel invitation (only by inviter)
    - respond: Accept or reject invitation (only by invited user)
    
    Filtering:
    - ?status=pending/accepted/rejected
    - ?event=<event_id>
    - ?type=received (default) or sent
    """
    
    permission_classes = [IsAuthenticated, IsInvitedUserOrInviterOrReadOnly]
    
    def get_queryset(self) -> QuerySet[EventInvitation]:
        """
        Get invitations based on user role and filters.
        
        Returns:
            QuerySet: Filtered invitations.
        """
        user = self.request.user
        queryset = EventInvitation.objects.select_related(
            'event', 'invited_user', 'invited_by',
            'event__organizer', 'event__city', 'event__country'
        ).prefetch_related('event__categories')
        
        invitation_type = self.request.query_params.get(
            QUERY_PARAM_TYPE, 
            INVITATION_TYPE_RECEIVED
        )
        
        if invitation_type == INVITATION_TYPE_SENT:
            queryset = queryset.filter(invited_by=user)
        else:  
            queryset = queryset.filter(invited_user=user)
        
        status_filter = self.request.query_params.get(QUERY_PARAM_STATUS)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        event_id = self.request.query_params.get(QUERY_PARAM_EVENT)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self) -> Type[Serializer]:
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class.
        """
        if self.action == 'list':
            return EventInvitationListSerializer
        elif self.action == 'create':
            return EventInvitationCreateSerializer
        elif self.action == 'respond':
            return EventInvitationResponseSerializer
        return EventInvitationSerializer
    
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new invitation.
        
        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: Created invitation data or error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        
        response_serializer = EventInvitationSerializer(invitation)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Disable update method.
        
        Use respond action instead for accepting/rejecting invitations.
        
        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: Error message with 405 status.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject invitations'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Disable partial update method.
        
        Use respond action instead for accepting/rejecting invitations.
        
        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: Error message with 405 status.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject invitations'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Cancel/delete an invitation.
        
        Only the inviter or event organizer can cancel invitations.
        Cannot cancel already accepted/rejected invitations.
        
        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: Success or error message.
        """
        invitation = self.get_object()
        
        if request.user not in [invitation.invited_by, invitation.event.organizer]:
            return Response(
                {'detail': 'Only the inviter or event organizer can cancel invitations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if invitation.status != INVITATION_STATUS_PENDING:
            return Response(
                {'detail': f'Cannot cancel invitation with status: {invitation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInvitedUser])
    def respond(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Respond to an invitation (accept or reject).
        
        Only the invited user can respond.
        
        Request body:
            {
                "action": "accept" or "reject"
            }
        
        Args:
            request: The request object.
            pk: Invitation ID.
            
        Returns:
            Response: Updated invitation data or error.
        """
        invitation = self.get_object()
        
        serializer = EventInvitationResponseSerializer(
            invitation,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        
        response_serializer = EventInvitationSerializer(invitation)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request: Request) -> Response:
        """
        Get all pending invitations for the current user.
        
        Args:
            request: The request object.
            
        Returns:
            Response: List of pending invitations.
        """
        queryset = self.get_queryset().filter(status=INVITATION_STATUS_PENDING)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventInvitationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventInvitationListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request: Request) -> Response:
        """
        Get invitation statistics for the current user.
        
        Returns counts of pending, accepted, and rejected invitations.
        
        Args:
            request: The request object.
            
        Returns:
            Response: Statistics dictionary.
        """
        user = request.user
        
        received = EventInvitation.objects.filter(invited_user=user)
        sent = EventInvitation.objects.filter(invited_by=user)
        
        stats: Dict[str, Dict[str, int]] = {
            'received': {
                'total': received.count(),
                'pending': received.filter(status=INVITATION_STATUS_PENDING).count(),
                'accepted': received.filter(status=INVITATION_STATUS_ACCEPTED).count(),
                'rejected': received.filter(status=INVITATION_STATUS_REJECTED).count(),
            },
            'sent': {
                'total': sent.count(),
                'pending': sent.filter(status=INVITATION_STATUS_PENDING).count(),
                'accepted': sent.filter(status=INVITATION_STATUS_ACCEPTED).count(),
                'rejected': sent.filter(status=INVITATION_STATUS_REJECTED).count(),
            }
        }
        
        return Response(stats)