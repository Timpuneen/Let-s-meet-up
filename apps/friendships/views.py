"""
Views for Friendship management.

This module contains ViewSets for creating, viewing, and responding
to friend requests with proper permissions and filtering.
"""

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import UserSerializer
from apps.users.models import User

from .models import Friendship, FRIENDSHIP_STATUS_PENDING, FRIENDSHIP_STATUS_ACCEPTED
from .serializers import (
    FriendshipSerializer,
    FriendshipListSerializer,
    FriendshipCreateSerializer,
    FriendshipResponseSerializer,
)
from .permissions import (
    IsSenderOrReceiverOrReadOnly,
    IsReceiver,
)


class FriendshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing friendships.
    
    Provides CRUD operations for friendships with filtering:
    - List: Shows friendships involving the current user
    - Create: Send friend request to a user
    - Retrieve: View friendship details
    - Update: Not allowed (use respond action instead)
    - Delete: Remove friendship or cancel request
    - respond: Accept or reject friend request (only by receiver)
    - friends: List all friends (accepted friendships)
    
    Filtering:
    - ?status=pending/accepted/rejected
    - ?type=received (default) or sent
    """
    
    permission_classes = [IsAuthenticated, IsSenderOrReceiverOrReadOnly]
    
    def get_queryset(self):
        """
        Get friendships based on user role and filters.
        
        Returns:
            QuerySet: Filtered friendships.
        """
        user = self.request.user
        queryset = Friendship.objects.select_related('sender', 'receiver')
        
        # ВСЕГДА показывать все связи, где пользователь участвует
        # (для безопасности полагаемся на permissions)
        queryset = queryset.filter(Q(sender=user) | Q(receiver=user))
        
        # Фильтры для list action (чтобы сохранить функциональность)
        if self.action == 'list':
            friendship_type = self.request.query_params.get('type', 'received')
            
            if friendship_type == 'sent':
                queryset = queryset.filter(sender=user)
            elif friendship_type == 'received':
                queryset = queryset.filter(receiver=user)
            # 'all' уже включено в базовый фильтр Q(sender=user) | Q(receiver=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class.
        """
        if self.action == 'list':
            return FriendshipListSerializer
        elif self.action == 'create':
            return FriendshipCreateSerializer
        elif self.action == 'respond':
            return FriendshipResponseSerializer
        elif self.action == 'friends':
            return UserSerializer
        return FriendshipSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new friend request.
        
        Args:
            request: The request object.
            
        Returns:
            Response: Created friendship data or error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friendship = serializer.save()
        
        # Return full friendship data
        response_serializer = FriendshipSerializer(friendship)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Disable update method.
        
        Use respond action instead for accepting/rejecting requests.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject friend requests'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Disable partial update method.
        
        Use respond action instead for accepting/rejecting requests.
        """
        return Response(
            {'detail': 'Use the "respond" action to accept or reject friend requests'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove friendship or cancel friend request.
        
        - Sender can cancel pending requests
        - Either user can remove accepted friendship
        - Receiver can reject pending request (better use respond action)
        
        Args:
            request: The request object.
            
        Returns:
            Response: Success or error message.
        """
        friendship = self.get_object()
        user = request.user
        
        # Check permissions
        if user not in [friendship.sender, friendship.receiver]:
            return Response(
                {'detail': 'You are not involved in this friendship'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete the friendship
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsReceiver])
    def respond(self, request, pk=None):
        """
        Respond to a friend request (accept or reject).
        
        Only the receiver can respond.
        
        Request body:
            {
                "action": "accept" or "reject"
            }
        
        Args:
            request: The request object.
            pk: Friendship ID.
            
        Returns:
            Response: Updated friendship data or error.
        """
        friendship = self.get_object()
        
        serializer = FriendshipResponseSerializer(
            friendship,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        friendship = serializer.save()
        
        # Return full friendship data
        response_serializer = FriendshipSerializer(friendship)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending friend requests for the current user.
        
        Args:
            request: The request object.
            
        Returns:
            Response: List of pending requests.
        """
        queryset = self.get_queryset().filter(
            receiver=request.user,
            status=FRIENDSHIP_STATUS_PENDING
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FriendshipListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FriendshipListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def friends(self, request):
        """
        Get all friends of the current user (accepted friendships only).
        
        Returns user objects, not friendship objects.
        
        Args:
            request: The request object.
            
        Returns:
            Response: List of friends.
        """
        user = request.user
        
        # Get all accepted friendships
        friendships = Friendship.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status=FRIENDSHIP_STATUS_ACCEPTED
        ).select_related('sender', 'receiver')
        
        # Extract friend users
        friends = []
        for friendship in friendships:
            friend = friendship.receiver if friendship.sender == user else friendship.sender
            friends.append(friend)
        
        page = self.paginate_queryset(friends)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get friendship statistics for the current user.
        
        Returns counts of pending, accepted, and rejected requests.
        
        Args:
            request: The request object.
            
        Returns:
            Response: Statistics dictionary.
        """
        user = request.user
        
        sent = Friendship.objects.filter(sender=user)
        received = Friendship.objects.filter(receiver=user)
        friends = Friendship.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        stats = {
            'friends_count': friends.count(),
            'sent': {
                'total': sent.count(),
                'pending': sent.filter(status=FRIENDSHIP_STATUS_PENDING).count(),
                'accepted': sent.filter(status=FRIENDSHIP_STATUS_ACCEPTED).count(),
                'rejected': sent.filter(status='rejected').count(),
            },
            'received': {
                'total': received.count(),
                'pending': received.filter(status=FRIENDSHIP_STATUS_PENDING).count(),
                'accepted': received.filter(status=FRIENDSHIP_STATUS_ACCEPTED).count(),
                'rejected': received.filter(status='rejected').count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def check(self, request):
        """
        Check friendship status with another user.
        
        Request body:
            {
                "user_email": "friend@example.com"
            }
        
        Args:
            request: The request object.
            
        Returns:
            Response: Friendship status information.
        """
        user_email = request.data.get('user_email')
        if not user_email:
            return Response(
                {'detail': 'user_email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            other_user = User.objects.get(email=user_email, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if other_user == request.user:
            return Response({
                'status': 'self',
                'message': 'This is your own account'
            })
        
        # Check friendship in both directions
        friendship = Friendship.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).first()
        
        if not friendship:
            return Response({
                'status': 'none',
                'message': 'No friendship exists',
                'can_send_request': True
            })
        
        response_data = {
            'status': friendship.status,
            'friendship_id': friendship.id,
        }
        
        if friendship.status == FRIENDSHIP_STATUS_PENDING:
            if friendship.sender == request.user:
                response_data['message'] = 'Friend request sent (waiting for response)'
                response_data['can_cancel'] = True
            else:
                response_data['message'] = 'Friend request received (you can respond)'
                response_data['can_respond'] = True
        elif friendship.status == FRIENDSHIP_STATUS_ACCEPTED:
            response_data['message'] = 'You are friends'
            response_data['can_unfriend'] = True
        else:  # rejected
            response_data['message'] = 'Friend request was rejected'
            response_data['can_send_request'] = True
        
        return Response(response_data)