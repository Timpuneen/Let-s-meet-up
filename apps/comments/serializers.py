from typing import Any, Dict, List

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.comments.models import EventComment
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for EventComment model.
    
    Provides complete comment information including user details,
    depth level, and reply count for read operations.
    """
    
    user = UserSerializer(read_only=True)
    depth = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EventComment
        fields = [
            'id',
            'event',
            'user',
            'parent',
            'content',
            'depth',
            'reply_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_depth(self, obj: EventComment) -> int:
        """
        Get the depth of this comment in the thread.
        
        Args:
            obj (EventComment): The comment instance.
        
        Returns:
            int: Depth level (0 for top-level comments).
        """
        return obj.get_depth()
    
    def get_reply_count(self, obj: EventComment) -> int:
        """
        Get the total number of replies to this comment.
        
        Args:
            obj (EventComment): The comment instance.
        
        Returns:
            int: Number of direct and nested replies.
        """
        return obj.get_reply_count()


class CommentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing EventComment instances.
    
    Provides a summary view of comments for list endpoints,
    including essential information without nested details.
    """
    
    user = UserSerializer(read_only=True)
    depth = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EventComment
        fields = [
            'id',
            'event',
            'user',
            'parent',
            'content',
            'depth',
            'reply_count',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_depth(self, obj: EventComment) -> int:
        """Get the depth of this comment in the thread."""
        return obj.get_depth()
    
    def get_reply_count(self, obj: EventComment) -> int:
        """Get the total number of replies to this comment."""
        return obj.get_reply_count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating EventComment instances.
    
    Handles validation and serialization for comment creation.
    The user is automatically set from the request context.
    """
    
    class Meta:
        model = EventComment
        fields = ['event', 'parent', 'content']
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate comment data.
        
        Ensures that:
        - Parent comment exists if provided.
        - Parent comment belongs to the same event.
        
        Args:
            data (dict): Validated field data.
        
        Returns:
            dict: Validated data.
        
        Raises:
            ValidationError: If validation fails.
        """
        parent = data.get('parent')
        event = data.get('event')
        
        if parent:
            if not EventComment.objects.filter(id=parent.id).exists():
                raise ValidationError({'parent': 'Parent comment does not exist'})
            
            if parent.event != event:
                raise ValidationError({
                    'parent': 'Parent comment must belong to the same event'
                })
        
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> EventComment:
        """
        Create a new EventComment instance.
        
        The user is automatically set from the request context.
        
        Args:
            validated_data (dict): Validated data for the new comment.
        
        Returns:
            EventComment: The created EventComment instance.
        """
        return EventComment.objects.create(**validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating EventComment instances.
    
    Handles validation for comment updates.
    Only the content field can be updated.
    """
    
    class Meta:
        model = EventComment
        fields = ['content']
    
    def update(self, instance: EventComment, validated_data: Dict[str, Any]) -> EventComment:
        """
        Update an existing EventComment instance.
        
        Args:
            instance (EventComment): The EventComment instance to update.
            validated_data (dict): Validated data for the update.
        
        Returns:
            EventComment: The updated EventComment instance.
        """
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class NestedReplySerializer(serializers.ModelSerializer):
    """
    Recursive serializer for nested replies.
    
    Provides a tree structure of comments with all nested replies.
    Used for displaying threaded conversations.
    """
    
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()
    
    class Meta:
        model = EventComment
        fields = [
            'id',
            'event',
            'user',
            'parent',
            'content',
            'depth',
            'replies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_depth(self, obj: EventComment) -> int:
        """Get the depth of this comment in the thread."""
        return obj.get_depth()
    
    def get_replies(self, obj: EventComment) -> List[Dict[str, Any]]:
        """
        Get all direct replies to this comment.
        
        Args:
            obj (EventComment): The comment instance.
        
        Returns:
            list: Serialized nested replies.
        """
        replies = obj.replies.all().order_by('created_at')
        return NestedReplySerializer(replies, many=True).data

