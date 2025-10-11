from django.db import models
from django.conf import settings


class Event(models.Model):
    """
    Модель мероприятия
    - title: название мероприятия
    - description: описание
    - date: дата и время проведения
    - organizer: организатор (ForeignKey на User)
    - participants: участники (ManyToMany на User)
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    date = models.DateTimeField(verbose_name='Дата и время проведения')
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Организатор'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='registered_events',
        blank=True,
        verbose_name='Участники'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-date']
    
    def __str__(self):
        return self.title
