from django.db import models
from django.utils import timezone

class SoftDeletableManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    """
    def get_queryset(self):
        """Return only non-deleted records."""
        return super().get_queryset().filter(is_deleted=False)
    
class AllObjectsManager(models.Manager):
    """
    Manager that returns all records, including soft-deleted ones.
    """
    def get_queryset(self):
        """Return all records, including deleted ones."""
        return super().get_queryset()

class AbstractSoftDeletableModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Is Deleted',
    )
    deleted_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Deleted At',
    )

    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_deleted', 'deleted_at'])
        return (0, {})
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object from the database."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])