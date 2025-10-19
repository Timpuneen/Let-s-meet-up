from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from abstracts.models import AbstractSoftDeletableModel

class UserManager(BaseUserManager):
    """Manager for working with user model"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def create_user(self, email, name, password=None):
        """Create a regular user"""
        if not email:
            raise ValueError('Email is required for the user')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)  # Automatically hashes the password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None):
        """Create a superuser"""
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AllUsersManager(BaseUserManager):
    """Manager that returns all users, including soft-deleted ones"""
    
    def get_queryset(self):
        return super().get_queryset()

class User(AbstractBaseUser, PermissionsMixin, AbstractSoftDeletableModel):
    """
    Custom user model with soft delete functionality.
    - email: unique email (used for login)
    - name: user name
    - password: hashed password (automatically through set_password)
    - is_deleted: soft delete flag (inherited)
    - deleted_at: timestamp of deletion (inherited)
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    all_objects = AllUsersManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
