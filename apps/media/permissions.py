from typing import Set
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.media.models import EventPhoto

UPDATE_METHODS: Set[str] = {"PUT", "PATCH"}
DELETE_METHOD: str = "DELETE"
CREATE_METHOD: str = "POST"


class IsPhotoUploaderOrOrganizerOrAdmin(BasePermission):
    """
    Custom permission for photo operations.
    
    Permission Rules:
    - Read operations (GET, HEAD, OPTIONS): Allowed for any authenticated user
    - Create operations (POST): Allowed for event participants and organizer
    - Update operations (PUT, PATCH): Only for photo uploader
    - Delete operations (DELETE): For photo uploader, event organizer, or admin users
    
    This permission ensures proper access control for photo management
    while allowing flexibility for event organizers and administrators.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return True if the request has an authenticated user."""
        return bool(getattr(request, "user", None) and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: EventPhoto) -> bool:
        """
        Check if the user has permission to perform the action on a specific photo.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The photo object being accessed.
        
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in SAFE_METHODS:
            return True
        
        if request.method in UPDATE_METHODS:
            return obj.uploaded_by == request.user
        
        if request.method == DELETE_METHOD:
            return (
                obj.uploaded_by == request.user or
                obj.event.organizer == request.user or
                request.user.is_staff
            )
        
        return False


class IsEventOrganizerOrAdmin(BasePermission):
    """
    Custom permission for cover photo management.
    
    Only event organizers and admins can set/remove cover photos.
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: EventPhoto) -> bool:
        """
        Check if the user can manage cover photo status.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The photo object being accessed.
        
        Returns:
            bool: True if user is event organizer or admin, False otherwise.
        """
        return obj.event.organizer == request.user or request.user.is_staff

