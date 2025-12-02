from typing import Tuple, Dict

from django.db import models
from django.utils import timezone


class SoftDeletableManager(models.Manager):
    """
    Unified manager for soft-deletable models.
    
    By default, filters out soft-deleted records. Use with_deleted()
    to include deleted objects in querysets.
    
    Examples:
        Model.objects.all()   Only non-deleted objects
        Model.objects.with_deleted()   All objects including deleted
        Model.objects.deleted_only()   Only deleted objects
    """
    
    def get_queryset(self) -> models.QuerySet:
        """
        Return only non-deleted records by default.
        
        Returns:
            QuerySet: Filtered queryset excluding soft-deleted objects.
        """
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self) -> models.QuerySet:
        """
        Return all records including soft-deleted ones.
        
        Returns:
            QuerySet: Unfiltered queryset with all objects.
        """
        return super().get_queryset()
    
    def deleted_only(self) -> models.QuerySet:
        """
        Return only soft-deleted records.
        
        Returns:
            QuerySet: Filtered queryset with only deleted objects.
        """
        return super().get_queryset().filter(is_deleted=True)


class AbstractSoftDeletableModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    
    Instead of permanently deleting records from the database,
    this model marks them as deleted and records the deletion timestamp.
    
    Attributes:
        is_deleted (bool): Flag indicating if the object is soft-deleted.
        deleted_at (datetime): Timestamp when the object was soft-deleted.
    
    Managers:
        objects: Returns only non-deleted objects.
        all_objects: Returns all objects including deleted ones.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Is Deleted',
        help_text='Indicates if this record has been soft-deleted',
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deleted At',
        help_text='Timestamp when this record was soft-deleted',
    )

    objects = SoftDeletableManager()

    class Meta:
        abstract = True

    def delete(
        self,
        using: str | None = None,
        keep_parents: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """
        Soft delete the object by marking it as deleted.
        
        Args:
            using: Database alias to use for the operation.
            keep_parents: Ignored for soft delete operations.
        
        Returns:
            Tuple containing (0, {}) to maintain compatibility with Django's delete.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_deleted', 'deleted_at'])
        return (0, {})

    def hard_delete(
        self,
        using: str | None = None,
        keep_parents: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """
        Permanently delete the object from the database.
        
        This performs a real database deletion and cannot be undone.
        
        Args:
            using: Database alias to use for the operation.
            keep_parents: Whether to keep parent model instances.
        
        Returns:
            Tuple containing deletion count and dict of deleted objects by type.
        """
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """
        Restore a soft-deleted object.
        
        Clears the is_deleted flag and deleted_at timestamp,
        making the object visible through the default manager again.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class AbstractTimestampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    
    Automatically tracks when records are created and last updated.
    
    Attributes:
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Timestamp when this record was created',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Timestamp when this record was last updated',
    )

    class Meta:
        abstract = True