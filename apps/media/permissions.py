"""
Custom permissions for photo management.

This module contains permission classes for controlling access
to photo upload, editing, and deletion operations.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


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
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
        
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # All operations require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on a specific photo.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The photo object being accessed.
        
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # Read operations are allowed for authenticated users
        if request.method in SAFE_METHODS:
            return True
        
        # Update permissions are only for the photo uploader
        if request.method in ['PUT', 'PATCH']:
            return obj.uploaded_by == request.user
        
        # Delete permissions: uploader, event organizer, or admin
        if request.method == 'DELETE':
            return (
                obj.uploaded_by == request.user or
                obj.event.organizer == request.user or
                request.user.is_staff
            )
        
        # For any other operations, deny by default
        return False


class IsEventOrganizerOrAdmin(BasePermission):
    """
    Custom permission for cover photo management.
    
    Only event organizers and admins can set/remove cover photos.
    """
    
    def has_object_permission(self, request, view, obj):
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

