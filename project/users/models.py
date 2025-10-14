from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager for working with user model"""
    
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


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    - email: unique email (used for login)
    - name: user name
    - password: hashed password (automatically through set_password)
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
