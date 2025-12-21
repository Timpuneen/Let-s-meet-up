from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.participants.models import PARTICIPANT_STATUS_ACCEPTED, EventParticipant


class CanInviteToEvent(BasePermission):
    """
    Permission to check if user can invite others to an event.
    
    Used for CREATE operations on invitations.
    Checks event.can_user_invite() logic.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object.
            view: The view object.
            
        Returns:
            bool: True if user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user can invite to the event.
        
        Args:
            request: The request object.
            view: The view object.
            obj: EventInvitation instance.
            
        Returns:
            bool: True if user can invite, False otherwise.
        """
        return obj.event.can_user_invite(request.user)


class IsInvitedUserOrInviterOrReadOnly(BasePermission):
    """
    Permission allowing:
    - Read access to invited user and inviter
    - Write access (respond) only to invited user
    - Inviter can view but cannot modify
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object.
            view: The view object.
            
        Returns:
            bool: True if user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user is involved in the invitation.
        
        Args:
            request: The request object.
            view: The view object.
            obj: EventInvitation instance.
            
        Returns:
            bool: True if user can access invitation, False otherwise.
        """
        if request.method in SAFE_METHODS:
            return (
                request.user == obj.invited_user or
                request.user == obj.invited_by or
                request.user == obj.event.organizer
            )
        
        return request.user == obj.invited_user


class IsInvitedUser(BasePermission):
    """
    Permission allowing only the invited user to respond to invitation.
    
    Used for accept/reject actions.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object.
            view: The view object.
            
        Returns:
            bool: True if user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user is the invited user.
        
        Args:
            request: The request object.
            view: The view object.
            obj: EventInvitation instance.
            
        Returns:
            bool: True if user is invited user, False otherwise.
        """
        return request.user == obj.invited_user


class IsEventParticipant(BasePermission):
    """
    Permission to check if user is a participant of the event.
    
    Used to verify user can invite others based on event settings.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object.
            view: The view object.
            
        Returns:
            bool: True if user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user is a participant of the event.
        
        Args:
            request: The request object.
            view: The view object.
            obj: EventInvitation or Event instance.
            
        Returns:
            bool: True if user is participant, False otherwise.
        """
        event = obj.event if hasattr(obj, 'event') else obj
        
        if request.user == event.organizer:
            return True
        
        return EventParticipant.objects.filter(
            event=event,
            user=request.user,
            status=PARTICIPANT_STATUS_ACCEPTED
        ).exists()