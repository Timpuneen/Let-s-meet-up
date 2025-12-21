from typing import Any, Dict

from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from apps.events.serializers import EventListSerializer
from apps.participants.models import EventParticipant
from apps.users.models import User
from apps.users.serializers import UserSerializer

from .models import INVITATION_STATUS_PENDING, EventInvitation


INVITATION_ACTION_ACCEPT = 'accept'
INVITATION_ACTION_REJECT = 'reject'

VALID_INVITATION_ACTIONS = [INVITATION_ACTION_ACCEPT, INVITATION_ACTION_REJECT]


class EventInvitationSerializer(ModelSerializer):
    """
    Full serializer for EventInvitation model with all details.
    
    Provides complete invitation information including event details,
    invited user, inviter, and current status.
    Used for retrieve operations and detailed views.
    """

    event = EventListSerializer(read_only=True)
    invited_user = UserSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    
    class Meta:
        model = EventInvitation
        fields = [
            'id', 'event', 'invited_user', 'invited_by', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventInvitationListSerializer(ModelSerializer):
    """
    Simplified serializer for invitation list views.
    
    Provides essential invitation information for list operations.
    """

    event_title = SerializerMethodField()
    invited_user_name = SerializerMethodField()
    invited_by_name = SerializerMethodField()
    
    class Meta:
        model = EventInvitation
        fields = [
            'id', 'event', 'event_title', 
            'invited_user', 'invited_user_name',
            'invited_by', 'invited_by_name',
            'status', 'created_at'
        ]
    
    def get_event_title(self, obj: EventInvitation) -> str:
        """
        Get event title.
        
        Args:
            obj: EventInvitation instance.
            
        Returns:
            str: Event title.
        """
        return obj.event.title
    
    def get_invited_user_name(self, obj: EventInvitation) -> str:
        """
        Get invited user name.
        
        Args:
            obj: EventInvitation instance.
            
        Returns:
            str: User name.
        """
        return obj.invited_user.name
    
    def get_invited_by_name(self, obj: EventInvitation) -> str:
        """
        Get inviter name.
        
        Args:
            obj: EventInvitation instance.
            
        Returns:
            str: Inviter name.
        """
        return obj.invited_by.name


class EventInvitationCreateSerializer(ModelSerializer):
    """
    Serializer for creating new event invitations.
    
    Validates invitation data and ensures:
    - Inviter has permission to invite
    - Invited user can receive invitations
    - No duplicate invitations exist
    """
    
    invited_user_email = CharField(
        write_only=True,
        help_text='Email of the user to invite'
    )

    class Meta:
        model = EventInvitation
        fields = ['event', 'invited_user_email']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invitation creation.
        
        Args:
            data: Dictionary containing validated field data.
            
        Returns:
            dict: Validated data with invited_user added.
            
        Raises:
            ValidationError: If validation fails.
        """
        request = self.context.get('request')
        event = data.get('event')
        invited_user_email = data.get('invited_user_email')
        
        try:
            invited_user = User.objects.get(email=invited_user_email, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError({
                'invited_user_email': 'User with this email does not exist'
            })
        
        if event.is_deleted:
            raise ValidationError({'event': 'Cannot invite to a deleted event'})
        
        if not event.can_user_invite(request.user):
            raise ValidationError(
                'You do not have permission to invite users to this event'
            )
        
        if invited_user == event.organizer:
            raise ValidationError({
                'invited_user_email': 'Cannot invite the event organizer'
            })
        
        if EventParticipant.objects.filter(event=event, user=invited_user).exists():
            raise ValidationError({
                'invited_user_email': 'User is already a participant of this event'
            })
        
        if EventInvitation.objects.filter(event=event, invited_user=invited_user).exists():
            raise ValidationError({
                'invited_user_email': 'Invitation already exists for this user'
            })
        
        if not invited_user.can_be_invited_by(request.user):
            privacy = invited_user.get_invitation_privacy_display()
            raise ValidationError({
                'invited_user_email': f'User privacy settings ({privacy}) prevent invitations from you'
            })
        
        data['invited_user'] = invited_user
        data['invited_by'] = request.user
        
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> EventInvitation:
        """
        Create a new invitation.
        
        Args:
            validated_data: Dictionary containing validated invitation data.
            
        Returns:
            EventInvitation: The newly created invitation instance.
        """
        validated_data.pop('invited_user_email', None)
        
        return EventInvitation.objects.create(**validated_data)


class EventInvitationResponseSerializer(ModelSerializer):
    """
    Serializer for responding to invitations (accept/reject).
    
    Used for PATCH requests to update invitation status.
    """
    
    action = CharField(
        write_only=True,
        help_text='Action to perform: "accept" or "reject"'
    )

    class Meta:
        model = EventInvitation
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
        if value not in VALID_INVITATION_ACTIONS:
            raise ValidationError(
                f'Action must be one of: {", ".join(VALID_INVITATION_ACTIONS)}'
            )
        return value
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invitation response.
        
        Args:
            data: Dictionary containing validated field data.
            
        Returns:
            dict: Validated data.
            
        Raises:
            ValidationError: If validation fails.
        """
        invitation = self.instance
        
        if invitation.status != INVITATION_STATUS_PENDING:
            raise ValidationError(
                f'Cannot respond to invitation with status: {invitation.status}'
            )
        
        if data['action'] == INVITATION_ACTION_ACCEPT and invitation.event.is_full():
            raise ValidationError('Event has reached maximum capacity')
        
        return data
    
    def update(self, instance: EventInvitation, validated_data: Dict[str, Any]) -> EventInvitation:
        """
        Update invitation status based on action.
        
        Args:
            instance: Existing invitation instance.
            validated_data: Dictionary containing validated update data.
            
        Returns:
            EventInvitation: The updated invitation instance.
        """
        action = validated_data.get('action')
        
        if action == INVITATION_ACTION_ACCEPT:
            instance.accept()
        elif action == INVITATION_ACTION_REJECT:
            instance.reject()
        
        return instance