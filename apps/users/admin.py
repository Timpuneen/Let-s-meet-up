from typing import Any, Tuple, List, NamedTuple
from django.contrib.admin import SimpleListFilter, register, action
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import (
    RangeDateTimeFilter,
)
from import_export.admin import ImportExportModelAdmin

from .models import User


class AdminColors(NamedTuple):
    """Color constants for admin UI styling."""
    link: str = '#8b5cf6'
    muted: str = '#9ca3af'
    grey: str = '#6b7280'
    active: str = '#22c55e'
    inactive: str = '#ef4444'


class BadgeStyles(NamedTuple):
    """Badge styling constants."""
    superuser_bg: str = '#ef4444'
    staff_bg: str = '#8b5cf6'
    padding: str = '2px 8px'
    border_radius: str = '4px'
    font_size: str = '10px'
    margin_left: str = '8px'
    template: str = '<span style="background:{bg};color:white;padding:{padding};border-radius:{radius};font-size:{font_size};margin-left:{margin};">{label}</span>'
    superuser_label: str = 'SUPERUSER'
    staff_label: str = 'STAFF'


class StatsStyles(NamedTuple):
    """Statistics panel styling constants."""
    bg: str = '#f9fafb'
    container_padding: str = '15px'
    border_color: str = '#e5e7eb'
    heading_color: str = '#374151'
    heading_font_size: str = '14px'
    heading_margin: str = '0 0 15px 0'
    cell_padding: str = '8px 0'
    cell_text_color: str = '#111827'
    muted_color: str = '#6b7280'
    separator_width: str = '2px'
    border_radius: str = '8px'
    border_width: str = '1px'


class AdminLabels(NamedTuple):
    """Label constants for admin UI."""
    zero_events: str = '0 events'
    zero_friends: str = '0 friends'
    never: str = 'Never'


COLORS = AdminColors()
BADGE = BadgeStyles()
STATS = StatsStyles()
LABELS = AdminLabels()

LINK_STYLE_TEMPLATE = 'color:{};font-weight:500;'
HAS_COUNT_THRESHOLD = 0


class ActiveUsersFilter(SimpleListFilter):
    """Filter users by activity status."""
    title = _('Activity Status')
    parameter_name = 'activity'

    def lookups(self, request: HttpRequest, model_admin: Any) -> Tuple[Tuple[str, str], ...]:
        """Return filter choices for activity status."""
        return (
            ('active', _('Active Users')),
            ('inactive', _('Inactive Users')),
            ('staff', _('Staff Members')),
            ('superusers', _('Superusers')),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        """Filter queryset based on selected activity value."""
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_staff=False)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'staff':
            return queryset.filter(is_staff=True)
        if self.value() == 'superusers':
            return queryset.filter(is_superuser=True)
        return queryset


class EventOrganizersFilter(SimpleListFilter):
    """Filter users who have organized events."""
    title = _('Event Organizers')
    parameter_name = 'has_events'

    def lookups(self, request: HttpRequest, model_admin: Any) -> Tuple[Tuple[str, str], ...]:
        """Return filter choices for whether a user has organized events."""
        return (
            ('yes', _('Has Organized Events')),
            ('no', _('No Events Organized')),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        """Filter users by whether they've organized events."""
        if self.value() == 'yes':
            return queryset.annotate(
                event_count=Count('organized_events')
            ).filter(event_count__gt=HAS_COUNT_THRESHOLD)
        if self.value() == 'no':
            return queryset.annotate(
                event_count=Count('organized_events')
            ).filter(event_count=HAS_COUNT_THRESHOLD)
        return queryset


@register(User)
class UserAdmin(ImportExportModelAdmin, ModelAdmin):
    """Enhanced admin interface for User model with statistics and filters."""
    
    list_display = [
        'email_with_badge',
        'name',
        'activity_status',
        'invitation_privacy_badge',
        'organized_events_count',
        'participations_count',
        'friends_count',
        'joined_date',
    ]
    
    list_filter = [
        ActiveUsersFilter,
        EventOrganizersFilter,
        'invitation_privacy',
        ('created_at', RangeDateTimeFilter),
        ('last_login', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'email',
        'name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login',
        'user_statistics',
    ]
    
    autocomplete_fields = []
    
    fieldsets = (
        (_('Account Information'), {
            'fields': (
                'email',
                'password',
                'user_statistics',
            ),
            'description': 'Basic account credentials and information',
        }),
        (_('Personal Information'), {
            'fields': (
                'name',
                'invitation_privacy',
            ),
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ['collapse'],
        }),
        (_('Important Dates'), {
            'fields': (
                'last_login',
                'created_at',
                'updated_at',
            ),
            'classes': ['collapse'],
        }),
    )
    
    add_fieldsets = (
        (_('Account Information'), {
            'fields': (
                'email',
                'password1',
                'password2',
            ),
        }),
        (_('Personal Information'), {
            'fields': (
                'name',
                'invitation_privacy',
            ),
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
    
    actions = [
        'activate_users',
        'deactivate_users',
        'make_staff',
        'remove_staff',
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        """Optimize queryset with annotations for counts used in list display and details."""
        qs: QuerySet[User] = super().get_queryset(request)
        return qs.annotate(
            events_count=Count('organized_events', distinct=True),
            participations_count=Count('event_participations', distinct=True),
            friendships_count=Count(
                'sent_friendships',
                filter=Q(sent_friendships__status='accepted'),
                distinct=True
            ) + Count(
                'received_friendships',
                filter=Q(received_friendships__status='accepted'),
                distinct=True
            ),
        )

    @display(description=_('Email'), ordering='email', header=True)
    def email_with_badge(self, obj: User) -> List[str]:
        """Display the user's email with badges indicating elevated permissions."""
        badges: List[str] = []
        if obj.is_superuser:
            badges.append(BADGE.template.format(
                bg=BADGE.superuser_bg, padding=BADGE.padding,
                radius=BADGE.border_radius, font_size=BADGE.font_size,
                margin=BADGE.margin_left, label=BADGE.superuser_label
            ))
        elif obj.is_staff:
            badges.append(BADGE.template.format(
                bg=BADGE.staff_bg, padding=BADGE.padding,
                radius=BADGE.border_radius, font_size=BADGE.font_size,
                margin=BADGE.margin_left, label=BADGE.staff_label
            ))

        return [mark_safe(f'<strong>{obj.email}</strong>{"".join(badges)}')]

    @display(description=_('Status'), ordering='is_active')
    def activity_status(self, obj: User) -> str:
        """Display activity status with color."""
        if obj.is_active:
            return format_html('<span style="color:{};">● Active</span>', COLORS.active)
        return format_html('<span style="color:{};">● Inactive</span>', COLORS.inactive)

    @display(description=_('Privacy'), ordering='invitation_privacy')
    def invitation_privacy_badge(self, obj: User) -> str:
        """Display invitation privacy setting with an icon and color."""
        colors = {
            'everyone': COLORS.active,
            'friends': '#f59e0b',
            'none': COLORS.inactive,
        }
        icons = {
            'everyone': '🌍',
            'friends': '👥',
            'none': '🔒',
        }
        return format_html(
            '<span style="color:{};">{} {}</span>',
            colors.get(obj.invitation_privacy, COLORS.grey),
            icons.get(obj.invitation_privacy, ''),
            obj.get_invitation_privacy_display()
        )

    @display(description=_('Organized Events'), ordering='events_count')
    def organized_events_count(self, obj: User) -> str:
        """Display count of organized events, linking to the event changelist when present."""
        count = obj.events_count
        if count > HAS_COUNT_THRESHOLD:
            return format_html(
                '<a href="/admin/events/event/?organizer__id__exact={}" style="{}">{} events</a>',
                obj.pk,
                LINK_STYLE_TEMPLATE.format(COLORS.link),
                count
            )
        return format_html('<span style="color:{};">{}</span>', COLORS.muted, LABELS.zero_events)

    @display(description=_('Participations'), ordering='participations_count')
    def participations_count(self, obj: User) -> str:
        """Display count of event participations with a link to the participant changelist when present."""
        count = obj.participations_count
        if count > HAS_COUNT_THRESHOLD:
            return format_html(
                '<a href="/admin/participants/eventparticipant/?user__id__exact={}" style="{}">{} events</a>',
                obj.pk,
                LINK_STYLE_TEMPLATE.format(COLORS.link),
                count
            )
        return format_html('<span style="color:{};">{}</span>', COLORS.muted, LABELS.zero_events)

    @display(description=_('Friends'), ordering='friendships_count')
    def friends_count(self, obj: User) -> str:
        """Display number of accepted friendships with a link to the friendships changelist."""
        count = obj.friendships_count
        if count > HAS_COUNT_THRESHOLD:
            return format_html(
                '<a href="/admin/friendships/friendship/?q={}" style="{}">{} friends</a>',
                obj.email,
                LINK_STYLE_TEMPLATE.format(COLORS.link),
                count
            )
        return format_html('<span style="color:{};">{}</span>', COLORS.muted, LABELS.zero_friends)

    @display(description=_('Joined'), ordering='created_at')
    def joined_date(self, obj: User) -> str:
        """Return the formatted user creation date."""
        return obj.created_at.strftime('%b %d, %Y')

    @display(description=_('User Statistics'))
    def user_statistics(self, obj: User) -> str:
        """Return an HTML snippet summarizing the user's activity statistics."""
        if not obj.pk:
            return "Save user to see statistics"

        stats_html = f"""
        <div style="padding:{STATS.container_padding};background:{STATS.bg};border-radius:{STATS.border_radius};border:{STATS.border_width} solid {STATS.border_color};">
            <h3 style="margin:{STATS.heading_margin};color:{STATS.heading_color};font-size:{STATS.heading_font_size};">User Activity Overview</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Organized Events:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.organized_events.count()}</td>
                </tr>
                <tr>
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Event Participations:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.event_participations.count()}</td>
                </tr>
                <tr>
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Friendships:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.sent_friendships.filter(status='accepted').count() + obj.received_friendships.filter(status='accepted').count()}</td>
                </tr>
                <tr>
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Comments Posted:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.comments.count()}</td>
                </tr>
                <tr>
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Photos Uploaded:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.uploaded_photos.count()}</td>
                </tr>
                <tr style="border-top:{STATS.separator_width} solid {STATS.border_color};">
                    <td style="padding:{STATS.cell_padding};color:{STATS.muted_color};"><strong>Last Login:</strong></td>
                    <td style="text-align:right;color:{STATS.cell_text_color};">{obj.last_login.strftime('%b %d, %Y %H:%M') if obj.last_login else LABELS.never}</td>
                </tr>
            </table>
        </div>
        """
        return format_html(stats_html)

    @action(description=_('Activate selected users'))
    def activate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Bulk activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')

    @action(description=_('Deactivate selected users'))
    def deactivate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Bulk deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')

    @action(description=_('Grant staff permissions'))
    def make_staff(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Grant staff permissions to users."""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users granted staff permissions.')

    @action(description=_('Remove staff permissions'))
    def remove_staff(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Remove staff permissions from users."""
        updated = queryset.filter(is_superuser=False).update(is_staff=False)
        self.message_user(request, f'{updated} users had staff permissions removed.')
