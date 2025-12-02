"""
Permissions for Friendship management.

This module contains custom permission classes for friendship operations,
controlling who can view, create, and respond to friend requests.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSenderOrReceiverOrReadOnly(BasePermission):
    """
    Permission allowing:
    - Read access to sender and receiver
    - Write access (respond) only to receiver
    - Delete access for both sender and receiver
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is involved in the friendship.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Friendship instance.
            
        Returns:
            bool: True if user can access friendship, False otherwise.
        """
        # Разрешаем доступ, если пользователь является отправителем ИЛИ получателем
        if request.user not in [obj.sender, obj.receiver]:
            return False
        
        # Для безопасных методов (GET, HEAD, OPTIONS) - всегда разрешаем
        if request.method in SAFE_METHODS:
            return True
        
        # Для DELETE - разрешаем обоим пользователям
        if request.method == 'DELETE':
            return True
        
        # Для обновления (respond) - только получатель
        if request.method in ['PATCH', 'PUT', 'POST']:
            # Проверяем, это ли действие respond
            if hasattr(view, 'action') and view.action == 'respond':
                return request.user == obj.receiver
            
        return False


class IsReceiver(BasePermission):
    """
    Permission allowing only the receiver to respond to friendship request.
    
    Used for accept/reject actions.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the receiver.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Friendship instance.
            
        Returns:
            bool: True if user is receiver, False otherwise.
        """
        return request.user == obj.receiver


class IsSender(BasePermission):
    """
    Permission allowing only the sender to cancel their friend request.
    
    Used for canceling pending requests.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the sender.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Friendship instance.
            
        Returns:
            bool: True if user is sender, False otherwise.
        """
        return request.user == obj.sender