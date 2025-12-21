from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


HTTP_METHOD_DELETE = 'DELETE'
HTTP_METHOD_PATCH = 'PATCH'
HTTP_METHOD_PUT = 'PUT'
HTTP_METHOD_POST = 'POST'

WRITE_METHODS = [HTTP_METHOD_PATCH, HTTP_METHOD_PUT, HTTP_METHOD_POST]

VIEW_ACTION_RESPOND = 'respond'


class IsSenderOrReceiverOrReadOnly(BasePermission):
    """
    Permission allowing:
    - Read access to sender and receiver
    - Write access (respond) only to receiver
    - Delete access for both sender and receiver
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
        Check if user is involved in the friendship.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Friendship instance.
            
        Returns:
            bool: True if user can access friendship, False otherwise.
        """
        if request.user not in [obj.sender, obj.receiver]:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        if request.method == HTTP_METHOD_DELETE:
            return True
        
        if request.method in WRITE_METHODS:
            if hasattr(view, 'action') and view.action == VIEW_ACTION_RESPOND:
                return request.user == obj.receiver
            
        return False


class IsReceiver(BasePermission):
    """
    Permission allowing only the receiver to respond to friendship request.
    
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
        Check if user is the sender.
        
        Args:
            request: The request object.
            view: The view object.
            obj: Friendship instance.
            
        Returns:
            bool: True if user is sender, False otherwise.
        """
        return request.user == obj.sender