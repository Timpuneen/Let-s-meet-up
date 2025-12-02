from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from apps.abstracts.models import AbstractTimestampedModel, AbstractSoftDeletableModel, SoftDeletableManager


class EventComment(AbstractTimestampedModel, AbstractSoftDeletableModel):
    """
    Model representing a comment on an event.
    
    Supports threaded discussions through parent-child relationships,
    allowing users to reply to existing comments.
    
    Attributes:
        event (Event): The event this comment belongs to.
        user (User): User who posted the comment.
        parent (EventComment): Parent comment if this is a reply (optional).
        content (str): The comment text.
        created_at (datetime): When comment was posted (from AbstractTimestampedModel).
        updated_at (datetime): When comment was last edited (from AbstractTimestampedModel).
    """
    
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Event',
        help_text='Event this comment belongs to',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_comments',
        verbose_name='User',
        help_text='User who posted this comment',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Parent Comment',
        help_text='Parent comment if this is a reply',
    )
    content = models.TextField(
        verbose_name='Content',
        help_text='The comment text',
    )

    objects = SoftDeletableManager()
    
    class Meta:
        db_table = 'event_comments'
        verbose_name = 'Event Comment'
        verbose_name_plural = 'Event Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['event', 'created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the comment.
        
        Returns:
            str: User name and truncated content.
        """
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.user.name}: {content_preview}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed comment information.
        """
        return (
            f"EventComment(event_id={self.event_id}, user_id={self.user_id}, "
            f"parent_id={self.parent_id})"
        )
    
    def clean(self) -> None:
        """
        Validate the comment instance.
        
        Ensures that:
        - Parent comment belongs to the same event.
        - Comment is not its own parent.
        - Reply depth doesn't exceed reasonable limits.
        
        Raises:
            ValidationError: If validation fails.
        """
        if self.parent:
            if self.parent == self:
                raise ValidationError('Comment cannot be its own parent')
            
            if self.parent.event != self.event:
                raise ValidationError('Parent comment must belong to the same event')
            
            depth = 0
            current = self.parent
            max_depth = 10
            
            while current and depth < max_depth:
                depth += 1
                current = current.parent
            
            if depth >= max_depth:
                raise ValidationError(f'Reply depth cannot exceed {max_depth} levels')
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the comment instance after validation.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_depth(self) -> int:
        """
        Calculate the depth of this comment in the thread.
        
        Returns:
            int: Depth level (0 for top-level comments).
        """
        depth = 0
        current = self.parent
        
        while current:
            depth += 1
            current = current.parent
        
        return depth
    
    def get_thread_root(self) -> 'EventComment':
        """
        Get the root comment of this thread.
        
        Returns:
            EventComment: The top-level comment of this thread.
        """
        current = self
        
        while current.parent:
            current = current.parent
        
        return current
    
    def get_all_replies(self) -> models.QuerySet:
        """
        Get all replies to this comment (recursive).
        
        Returns:
            QuerySet: All descendant comments.
        """
        def get_replies_recursive(comment):
            """Helper function to recursively get all replies."""
            replies = list(comment.replies.all())
            all_replies = replies.copy()
            
            for reply in replies:
                all_replies.extend(get_replies_recursive(reply))
            
            return all_replies
        
        reply_ids = [r.id for r in get_replies_recursive(self)]
        return EventComment.objects.filter(id__in=reply_ids)
    
    def get_reply_count(self) -> int:
        """
        Get the total number of replies to this comment.
        
        Returns:
            int: Number of direct and nested replies.
        """
        return self.get_all_replies().count()