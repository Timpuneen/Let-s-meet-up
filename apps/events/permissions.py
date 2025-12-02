from typing import Any

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOrganizerOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow organizers to edit/delete events.
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        # Read permissions are allowed for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to the organizer
        return obj.organizer == request.user