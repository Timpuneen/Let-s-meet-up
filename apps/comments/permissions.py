from rest_framework.permissions import SAFE_METHODS, BasePermission
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
        return bool(request.user and request.user.is_authenticated)
    
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
        if request.method in SAFE_METHODS:
            return True
        
        return obj.user == request.user or request.user.is_staff