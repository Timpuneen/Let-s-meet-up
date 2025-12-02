from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import EventInvitation, INVITATION_STATUS_PENDING
from .serializers import (
    EventInvitationSerializer,
    EventInvitationListSerializer,
    EventInvitationCreateSerializer,
    EventInvitationResponseSerializer,
)
from .permissions import (
    IsInvitedUserOrInviterOrReadOnly,
    IsInvitedUser,
)


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
    
    def get_queryset(self):
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
        
        invitation_type = self.request.query_params.get('type', 'received')
        
        if invitation_type == 'sent':
            queryset = queryset.filter(invited_by=user)
        else:  
            queryset = queryset.filter(invited_user=user)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
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
    
    def create(self, request, *args, **kwargs):
        """
        Create a new invitation.
        
        Args:
            request: The request object.
            
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
    
    def update(self, request, *args, **kwargs):
        """
        Disable update method.
        
        Use respond action instead for accepting/rejecting invitations.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject invitations'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Disable partial update method.
        
        Use respond action instead for accepting/rejecting invitations.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject invitations'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Cancel/delete an invitation.
        
        Only the inviter or event organizer can cancel invitations.
        Cannot cancel already accepted/rejected invitations.
        
        Args:
            request: The request object.
            
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
    def respond(self, request, pk=None):
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
    def pending(self, request):
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
    def stats(self, request):
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
        
        stats = {
            'received': {
                'total': received.count(),
                'pending': received.filter(status=INVITATION_STATUS_PENDING).count(),
                'accepted': received.filter(status='accepted').count(),
                'rejected': received.filter(status='rejected').count(),
            },
            'sent': {
                'total': sent.count(),
                'pending': sent.filter(status=INVITATION_STATUS_PENDING).count(),
                'accepted': sent.filter(status='accepted').count(),
                'rejected': sent.filter(status='rejected').count(),
            }
        }
        
        return Response(stats)