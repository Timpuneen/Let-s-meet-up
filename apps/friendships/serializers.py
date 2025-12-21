from typing import Any, Dict

from django.db.models import Q
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from apps.users.models import User
from apps.users.serializers import UserSerializer

from .models import (
    FRIENDSHIP_STATUS_ACCEPTED,
    FRIENDSHIP_STATUS_PENDING,
    FRIENDSHIP_STATUS_REJECTED,
    Friendship,
)


FRIENDSHIP_ACTION_ACCEPT = 'accept'
FRIENDSHIP_ACTION_REJECT = 'reject'

VALID_FRIENDSHIP_ACTIONS = [FRIENDSHIP_ACTION_ACCEPT, FRIENDSHIP_ACTION_REJECT]


class FriendshipSerializer(ModelSerializer):
    """
    Full serializer for Friendship model with all details.
    
    Provides complete friendship information including sender and receiver details.
    Used for retrieve operations and detailed views.
    """

    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = Friendship
        fields = [
            'id', 'sender', 'receiver', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FriendshipListSerializer(ModelSerializer):
    """
    Simplified serializer for friendship list views.
    
    Provides essential friendship information for list operations.
    """

    sender_name = SerializerMethodField()
    sender_email = SerializerMethodField()
    receiver_name = SerializerMethodField()
    receiver_email = SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = [
            'id', 'sender', 'sender_name', 'sender_email',
            'receiver', 'receiver_name', 'receiver_email',
            'status', 'created_at'
        ]
    
    def get_sender_name(self, obj: Friendship) -> str:
        """
        Get sender name.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            str: Sender name.
        """
        return obj.sender.name
    
    def get_sender_email(self, obj: Friendship) -> str:
        """
        Get sender email.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            str: Sender email.
        """
        return obj.sender.email
    
    def get_receiver_name(self, obj: Friendship) -> str:
        """
        Get receiver name.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            str: Receiver name.
        """
        return obj.receiver.name
    
    def get_receiver_email(self, obj: Friendship) -> str:
        """
        Get receiver email.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            str: Receiver email.
        """
        return obj.receiver.email


class FriendshipCreateSerializer(ModelSerializer):
    """
    Serializer for creating new friendship requests.
    
    Validates friendship data and ensures:
    - Cannot send request to yourself
    - No duplicate requests exist
    - No opposite direction request exists
    """
    
    receiver_email = CharField(
        write_only=True,
        help_text='Email of the user to send friend request to'
    )

    class Meta:
        model = Friendship
        fields = ['receiver_email']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate friendship creation.
        
        Args:
            data: Dictionary containing validated field data.
            
        Returns:
            dict: Validated data with receiver added.
            
        Raises:
            ValidationError: If validation fails.
        """
        request = self.context.get('request')
        sender = request.user
        receiver_email = data.get('receiver_email')
        
        try:
            receiver = User.objects.get(email=receiver_email, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError({
                'receiver_email': 'User with this email does not exist'
            })
        
        if sender == receiver:
            raise ValidationError({
                'receiver_email': 'You cannot send friend request to yourself'
            })
        
        existing_friendship = Friendship.objects.filter(
            Q(sender=sender, receiver=receiver) | 
            Q(sender=receiver, receiver=sender)
        ).first()
        
        if existing_friendship:
            if existing_friendship.status == FRIENDSHIP_STATUS_PENDING:
                if existing_friendship.sender == sender:
                    raise ValidationError({
                        'receiver_email': 'Friend request already sent to this user'
                    })
                else:
                    raise ValidationError({
                        'receiver_email': 'This user has already sent you a friend request. Check your pending requests.'
                    })
            elif existing_friendship.status == FRIENDSHIP_STATUS_ACCEPTED:
                raise ValidationError({
                    'receiver_email': 'You are already friends with this user'
                })
        
        data['receiver'] = receiver
        data['sender'] = sender
        
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> Friendship:
        """
        Create a new friendship request.
        
        Args:
            validated_data: Dictionary containing validated friendship data.
            
        Returns:
            Friendship: The newly created friendship instance.
        """
        validated_data.pop('receiver_email', None)
        
        existing = Friendship.objects.filter(
            Q(sender=validated_data['sender'], receiver=validated_data['receiver']) |
            Q(sender=validated_data['receiver'], receiver=validated_data['sender']),
            status=FRIENDSHIP_STATUS_REJECTED
        ).first()
        
        if existing:
            existing.sender = validated_data['sender']
            existing.receiver = validated_data['receiver']
            existing.status = FRIENDSHIP_STATUS_PENDING
            existing.save()
            return existing
        
        return Friendship.objects.create(**validated_data)


class FriendshipResponseSerializer(ModelSerializer):
    """
    Serializer for responding to friendship requests (accept/reject).
    
    Used for PATCH requests to update friendship status.
    """
    
    action = CharField(
        write_only=True,
        help_text='Action to perform: "accept" or "reject"'
    )

    class Meta:
        model = Friendship
        fields = ['action']

    def validate_action(self, value: str) -> str:
        """
        Validate action value.
        
        Args:
            value: The action value.
            
        Returns:
            str: Validated action.
            
        Raises:
            ValidationError: If action is invalid.
        """
        if value not in VALID_FRIENDSHIP_ACTIONS:
            raise ValidationError(
                f'Action must be one of: {", ".join(VALID_FRIENDSHIP_ACTIONS)}'
            )
        return value
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate friendship response.
        
        Args:
            data: Dictionary containing validated field data.
            
        Returns:
            dict: Validated data.
            
        Raises:
            ValidationError: If validation fails.
        """
        friendship = self.instance
        
        if friendship.status != FRIENDSHIP_STATUS_PENDING:
            raise ValidationError(
                f'Cannot respond to friendship with status: {friendship.status}'
            )
        
        return data
    
    def update(self, instance: Friendship, validated_data: Dict[str, Any]) -> Friendship:
        """
        Update friendship status based on action.
        
        Args:
            instance: Existing friendship instance.
            validated_data: Dictionary containing validated update data.
            
        Returns:
            Friendship: The updated friendship instance.
        """
        action = validated_data.get('action')
        
        if action == FRIENDSHIP_ACTION_ACCEPT:
            instance.accept()
        elif action == FRIENDSHIP_ACTION_REJECT:
            instance.reject()
        
        return instance


class FriendSerializer(ModelSerializer):
    """
    Simplified serializer for listing friends (accepted friendships only).
    
    Returns user information of friends without friendship metadata.
    """
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at']