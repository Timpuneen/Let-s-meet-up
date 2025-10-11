from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""
    
    def create_user(self, email, name, password=None):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен для пользователя')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)  # Автоматически хеширует пароль
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None):
        """Создание суперпользователя"""
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя
    - email: уникальный email (используется для входа)
    - name: имя пользователя
    - password: хешированный пароль (автоматически через set_password)
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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
