from django.contrib.admin import register, action
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from django.http import HttpRequest
from django.db.models import QuerySet

from .models import EventInvitation

LINK_COLOR = '#8b5cf6'
MUTED_COLOR = '#6b7280'
STATUS_PENDING = 'pending'
STATUS_ACCEPTED = 'accepted'
STATUS_REJECTED = 'rejected'
STATUS_COLORS = {
    STATUS_PENDING: '#f59e0b',
    STATUS_ACCEPTED: '#22c55e',
    STATUS_REJECTED: '#ef4444',
}
STATUS_ICONS = {
    STATUS_PENDING: '⏳',
    STATUS_ACCEPTED: '✓',
    STATUS_REJECTED: '✗',
}
BADGE_STYLE_TEMPLATE = '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;font-size:11px;font-weight:500;">{} {}</span>'

DATE_TODAY_COLOR = '#22c55e'
DATE_RECENT_COLOR = '#f59e0b'
DATE_OLDER_COLOR = '#9ca3af'
DATE_FORMAT = '%b %d, %Y'
RECENT_DAYS = 7

@register(EventInvitation)
class EventInvitationAdmin(ModelAdmin):
    """Enhanced admin interface for Event Invitations."""
    
    list_display = [
        'event_link',
        'invited_user_link',
        'invited_by_link',
        'status_badge',
        'invitation_date',
    ]
    
    list_filter = [
        'status',
        ('event', RelatedDropdownFilter),
        ('invited_by', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'event__title',
        'invited_user__email',
        'invited_user__name',
        'invited_by__email',
        'invited_by__name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['event', 'invited_user', 'invited_by']
    
    fieldsets = (
        (_('Invitation Details'), {
            'fields': ('event', 'invited_user', 'invited_by', 'status'),
            'description': 'Manage event invitation details',
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )
    
    actions = [
        'accept_invitations',
        'reject_invitations',
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Return the queryset for event invitations with related objects for efficient admin display."""
        qs: QuerySet = super().get_queryset(request)
        return qs.select_related('event', 'invited_user', 'invited_by')

    
    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj: EventInvitation) -> str:
        """Return admin link to the related event."""
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:{};font-weight:500;">{}</a>',
            obj.event.pk,
            LINK_COLOR,
            obj.event.title
        )

    @display(description=_('Invited User'), ordering='invited_user__email')
    def invited_user_link(self, obj: EventInvitation) -> str:
        """Return admin link to the invited user."""
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:{};">{}</a>',
            obj.invited_user.pk,
            LINK_COLOR,
            obj.invited_user.name or obj.invited_user.email
        )

    @display(description=_('Invited By'), ordering='invited_by__email')
    def invited_by_link(self, obj: EventInvitation) -> str:
        """Return admin link to the user who sent the invitation."""
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:{};">{}</a>',
            obj.invited_by.pk,
            MUTED_COLOR,
            obj.invited_by.name or obj.invited_by.email
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj: EventInvitation) -> str:
        """Return a styled status badge for the invitation status."""
        color = STATUS_COLORS.get(obj.status, MUTED_COLOR)
        icon = STATUS_ICONS.get(obj.status, '')
        return format_html(BADGE_STYLE_TEMPLATE, color, icon, obj.get_status_display())

    @display(description=_('Invited On'), ordering='created_at')
    def invitation_date(self, obj: EventInvitation) -> str:
        """Return relative invited date with color indicating recentness."""
        from django.utils import timezone
        now = timezone.now()
        delta = now - obj.created_at

        if delta.days == 0:
            color = DATE_TODAY_COLOR
            text = 'Today'
        elif delta.days < RECENT_DAYS:
            color = DATE_RECENT_COLOR
            text = f'{delta.days}d ago'
        else:
            color = DATE_OLDER_COLOR
            text = obj.created_at.strftime(DATE_FORMAT)

        return format_html('<span style="color:{};">{}</span>', color, text)

    
    @action(description=_('Accept selected invitations'))
    def accept_invitations(self, request: HttpRequest, queryset: QuerySet[EventInvitation]) -> None:
        """Bulk accept selected pending invitations."""
        success_count = 0
        error_count = 0

        for invitation in queryset.filter(status=STATUS_PENDING):
            try:
                invitation.accept()
                success_count += 1
            except Exception:
                error_count += 1

        if success_count:
            self.message_user(
                request,
                f'{success_count} invitation(s) accepted successfully.',
                level=messages.SUCCESS
            )
        if error_count:
            self.message_user(
                request,
                f'{error_count} invitation(s) could not be accepted.',
                level=messages.WARNING
            )

    @action(description=_('Reject selected invitations'))
    def reject_invitations(self, request: HttpRequest, queryset: QuerySet[EventInvitation]) -> None:
        """Bulk reject selected pending invitations."""
        updated = queryset.filter(status=STATUS_PENDING).update(status=STATUS_REJECTED)
        self.message_user(
            request,
            f'{updated} invitation(s) rejected.',
            level=messages.SUCCESS
        )