"""
Custom permissions for comment management.

This module contains permission classes for controlling access
to comment creation, editing, and deletion operations.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.comments.models import EventComment


class IsCommentOwnerOrAdminOrReadOnly(BasePermission):
    """
    Custom permission for comment operations.
    
    Permission Rules:
    - Read operations (GET, HEAD, OPTIONS): Allowed for any authenticated user
    - Create operations (POST): Allowed for any authenticated user
    - Update/Delete operations (PUT, PATCH, DELETE): Only for comment owner or admin users
    
    This permission ensures that users can only modify or delete their own comments,
    unless they are administrators who have permissions to manage all comments.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the user has permission to perform the action.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
        
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # Allow read operations for authenticated users
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Allow create operations for authenticated users
        # Allow update/delete operations for authenticated users (object-level check below)
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request: Request, view: APIView, obj: EventComment) -> bool:
        """
        Check if the user has permission to perform the action on a specific comment.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The comment object being accessed.
        
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # Read operations are allowed for authenticated users
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the comment owner or admin users
        return obj.user == request.user or request.user.is_staff

