from typing import Any, List
from django.contrib.admin import register, action
from django.contrib import messages
from django.http import HttpRequest
from django.db.models.query import QuerySet
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventParticipant

LINK_COLOR = '#8b5cf6'
ADMIN_BADGE_BG = '#3b82f6'
MEMBER_BG = '#e5e7eb'
MEMBER_TEXT_COLOR = '#374151'
TODAY_COLOR = '#22c55e'
DAYS_AGO_COLOR = '#f59e0b'
BADGE_PADDING = '4px 10px'
BADGE_BORDER_RADIUS = '10px'
BADGE_FONT_SIZE = '11px'
BADGE_FONT_WEIGHT = '500'
JOINED_RECENT_DAYS = 7
TODAY_DAYS = 0
TODAY_LABEL = 'Today'
DAYS_AGO_TEMPLATE = '{} days ago'
ADMIN_BADGE_LABEL = '👑 Admin'
MEMBER_LABEL = 'Member'
LINK_STYLE_TEMPLATE = 'color:{};'

@register(EventParticipant)
class EventParticipantAdmin(ModelAdmin):
    """Admin interface for event participants (accepted members only)."""
    
    list_display = [
        'event_link',
        'user_link',
        'is_admin_badge',
        'joined_date',
    ]
    
    list_filter = [
        'is_admin',
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'event__title',
        'user__email',
        'user__name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at', 'status']
    
    autocomplete_fields = ['event', 'user']
    
    fieldsets = (
        (_('Participation Details'), {
            'fields': ('event', 'user', 'is_admin'),
            'description': 'Manage confirmed event participants',
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )
    
    actions = [
        'make_admin',
        'remove_admin',
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[EventParticipant]:
        """Return queryset optimized with select_related to avoid extra database queries."""
        qs: QuerySet[EventParticipant] = super().get_queryset(request)
        return qs.select_related('event', 'user')

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj: EventParticipant) -> str:
        """Return an admin link to the related event."""
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="{}">{}</a>',
            obj.event.pk,
            LINK_STYLE_TEMPLATE.format(LINK_COLOR),
            obj.event.title
        )

    @display(description=_('User'), ordering='user__email')
    def user_link(self, obj: EventParticipant) -> str:
        """Return an admin link to the related user."""
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:{}">{}</a>',
            obj.user.pk,
            LINK_COLOR,
            obj.user.name or obj.user.email
        )

    @display(description=_('Role'), ordering='is_admin')
    def is_admin_badge(self, obj: EventParticipant) -> str:
        """Return a badge indicating whether the participant is an admin."""
        if obj.is_admin:
            return format_html(
                '<span style="background:{};color:white;padding:{};border-radius:{};font-size:{};font-weight:{};">{}</span>',
                ADMIN_BADGE_BG,
                BADGE_PADDING,
                BADGE_BORDER_RADIUS,
                BADGE_FONT_SIZE,
                BADGE_FONT_WEIGHT,
                ADMIN_BADGE_LABEL
            )
        return format_html(
            '<span style="background:{};color:{};padding:{};border-radius:{};font-size:{};">{}</span>',
            MEMBER_BG,
            MEMBER_TEXT_COLOR,
            BADGE_PADDING,
            BADGE_BORDER_RADIUS,
            BADGE_FONT_SIZE,
            MEMBER_LABEL
        )

    @display(description=_('Joined'), ordering='created_at')
    def joined_date(self, obj: EventParticipant) -> str:
        """Return a human-friendly representation of the join date."""
        from django.utils import timezone
        now = timezone.now()
        delta = now - obj.created_at

        if delta.days == TODAY_DAYS:
            return format_html('<span style="color:{};">{}</span>', TODAY_COLOR, TODAY_LABEL)
        elif delta.days < JOINED_RECENT_DAYS:
            return format_html('<span style="color:{};">{}</span>', DAYS_AGO_COLOR, DAYS_AGO_TEMPLATE.format(delta.days))
        else:
            return obj.created_at.strftime('%b %d, %Y')

    @action(description=_('Grant admin privileges'))
    def make_admin(self, request: HttpRequest, queryset: QuerySet[EventParticipant]) -> None:
        """Grant admin privileges to selected participants."""
        updated = 0
        for participant in queryset.filter(is_admin=False):
            participant.make_admin()
            updated += 1

        self.message_user(
            request,
            f'{updated} participant(s) granted admin privileges.',
            level=messages.SUCCESS
        )

    @action(description=_('Remove admin privileges'))
    def remove_admin(self, request: HttpRequest, queryset: QuerySet[EventParticipant]) -> None:
        """Remove admin privileges from selected participants."""
        updated = 0
        for participant in queryset.filter(is_admin=True):
            participant.remove_admin()
            updated += 1

        self.message_user(
            request,
            f'{updated} participant(s) admin privileges removed.',
            level=messages.SUCCESS
        )