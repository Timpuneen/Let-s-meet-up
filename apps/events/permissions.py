from typing import Any

from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOrganizerOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow organizers to edit/delete events.
    
    Allows read access to all users (including unauthenticated).
    Write/delete access only for the event organizer.
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user has permission to access the object.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Event instance.
            
        Returns:
            bool: True if user can access, False otherwise.
        """
        if request.method in SAFE_METHODS:
            return True
        
        return obj.organizer == request.user