from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.abstracts.models import AbstractSoftDeletableModel, AbstractTimestampedModel, SoftDeletableManager
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED

MAX_EMAIL_LENGTH = 255
MAX_NAME_LENGTH = 255
INVITATION_PRIVACY_MAX_LENGTH = 20

INVITATION_PRIVACY_EVERYONE = 'everyone'
INVITATION_PRIVACY_FRIENDS = 'friends'
INVITATION_PRIVACY_NONE = 'none'

INVITATION_PRIVACY_CHOICES = [
    (INVITATION_PRIVACY_EVERYONE, 'Everyone'),
    (INVITATION_PRIVACY_FRIENDS, 'Friends Only'),
    (INVITATION_PRIVACY_NONE, 'Nobody'),
]


class UserManager(SoftDeletableManager, BaseUserManager):
    """
    Custom manager for the User model.
    
    Combines soft-delete filtering from SoftDeletableManager
    with user creation methods from BaseUserManager.
    
    Examples:
        User.objects.all()  # Only non-deleted users
        User.objects.with_deleted()  # All users including deleted
        User.objects.deleted_only()  # Only deleted users
    """
    
    def create_user(
        self,
        email: str,
        name: str,
        password: str | None = None,
        **extra_fields: Any
    ) -> 'User':
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email: User's email address (used for authentication).
            name: User's display name.
            password: User's password (will be hashed).
            **extra_fields: Additional fields to set on the user.
        
        Returns:
            User: The created user instance.
        
        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError('Email is required for the user')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(
        self,
        email: str,
        name: str,
        password: str | None = None,
        **extra_fields: Any
    ) -> 'User':
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email: Superuser's email address.
            name: Superuser's display name.
            password: Superuser's password (will be hashed).
            **extra_fields: Additional fields to set on the superuser.
        
        Returns:
            User: The created superuser instance.
        
        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AbstractSoftDeletableModel, AbstractTimestampedModel):
    """
    Custom user model with soft delete functionality.
    
    Uses email as the unique identifier for authentication instead of username.
    Includes invitation privacy settings to control who can invite the user to events.
    
    Attributes:
        email (str): Unique email address (used for login).
        name (str): User's display name.
        is_active (bool): Whether the user account is active.
        is_staff (bool): Whether the user can access the admin site.
        invitation_privacy (str): Who can invite this user to events.
        last_login (datetime): Last time the user logged in (from AbstractBaseUser).
        is_deleted (bool): Soft delete flag (from AbstractSoftDeletableModel).
        deleted_at (datetime): Deletion timestamp (from AbstractSoftDeletableModel).
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
        updated_at (datetime): Last update timestamp (from AbstractTimestampedModel).
    """
    
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Email Address',
        help_text='Unique email address used for authentication',
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Name',
        help_text="User's display name",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Designates whether this user should be treated as active',
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff Status',
        help_text='Designates whether the user can log into the admin site',
    )
    invitation_privacy = models.CharField(
        max_length=INVITATION_PRIVACY_MAX_LENGTH,
        choices=INVITATION_PRIVACY_CHOICES,
        default=INVITATION_PRIVACY_EVERYONE,
        verbose_name='Invitation Privacy',
        help_text='Controls who can invite this user to events',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the user.
        
        Returns:
            str: User's email address.
        """
        return self.email
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the user.
        
        Returns:
            str: Detailed user information.
        """
        return f"User(email={self.email}, name={self.name})"
    
    def can_be_invited_by(self, inviter: 'User') -> bool:
        """
        Check if this user can be invited to events by the given inviter.
        
        Args:
            inviter: The user attempting to send an invitation.
        
        Returns:
            bool: True if invitation is allowed, False otherwise.
        """
        if self.invitation_privacy == INVITATION_PRIVACY_EVERYONE:
            return True
        
        if self.invitation_privacy == INVITATION_PRIVACY_FRIENDS:
            return Friendship.objects.filter(
                models.Q(sender=self, receiver=inviter) | models.Q(sender=inviter, receiver=self),
                status=FRIENDSHIP_STATUS_ACCEPTED
            ).exists()
        
        return False