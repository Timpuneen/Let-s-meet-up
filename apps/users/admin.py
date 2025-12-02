from django.contrib import admin
from django.db.models import Count, Q
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


class ActiveUsersFilter(admin.SimpleListFilter):
    """Filter users by activity status."""
    title = _('Activity Status')
    parameter_name = 'activity'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active Users')),
            ('inactive', _('Inactive Users')),
            ('staff', _('Staff Members')),
            ('superusers', _('Superusers')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_staff=False)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'staff':
            return queryset.filter(is_staff=True)
        if self.value() == 'superusers':
            return queryset.filter(is_superuser=True)
        return queryset


class EventOrganizersFilter(admin.SimpleListFilter):
    """Filter users who have organized events."""
    title = _('Event Organizers')
    parameter_name = 'has_events'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has Organized Events')),
            ('no', _('No Events Organized')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(
                event_count=Count('organized_events')
            ).filter(event_count__gt=0)
        if self.value() == 'no':
            return queryset.annotate(
                event_count=Count('organized_events')
            ).filter(event_count=0)
        return queryset


@admin.register(User)
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

    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        qs = super().get_queryset(request)
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
    def email_with_badge(self, obj):
        """Display email with status badges."""
        badges = []
        if obj.is_superuser:
            badges.append('<span style="background:#ef4444;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-left:8px;">SUPERUSER</span>')
        elif obj.is_staff:
            badges.append('<span style="background:#3b82f6;color:white;padding:2px 8px;border-radius:4px;font-size:10px;margin-left:8px;">STAFF</span>')
        
        return [mark_safe(
            f'<strong>{obj.email}</strong>{"".join(badges)}'
        )]

    @display(description=_('Status'), ordering='is_active')
    def activity_status(self, obj):
        """Display activity status with color."""
        if obj.is_active:
            return format_html(
                '<span style="color:#22c55e;">● Active</span>'
            )
        return format_html(
            '<span style="color:#ef4444;">● Inactive</span>'
        )

    @display(description=_('Privacy'), ordering='invitation_privacy')
    def invitation_privacy_badge(self, obj):
        """Display invitation privacy setting with icon."""
        colors = {
            'everyone': '#22c55e',
            'friends': '#f59e0b',
            'none': '#ef4444',
        }
        icons = {
            'everyone': '🌍',
            'friends': '👥',
            'none': '🔒',
        }
        return format_html(
            '<span style="color:{};">{} {}</span>',
            colors.get(obj.invitation_privacy, '#6b7280'),
            icons.get(obj.invitation_privacy, ''),
            obj.get_invitation_privacy_display()
        )

    @display(description=_('Organized Events'), ordering='events_count')
    def organized_events_count(self, obj):
        """Display count of organized events."""
        count = obj.events_count
        if count > 0:
            return format_html(
                '<a href="/admin/events/event/?organizer__id__exact={}" style="color:#8b5cf6;font-weight:500;">{} events</a>',
                obj.pk,
                count
            )
        return format_html('<span style="color:#9ca3af;">0 events</span>')

    @display(description=_('Participations'), ordering='participations_count')
    def participations_count(self, obj):
        """Display count of event participations."""
        count = obj.participations_count
        if count > 0:
            return format_html(
                '<a href="/admin/participants/eventparticipant/?user__id__exact={}" style="color:#8b5cf6;font-weight:500;">{} events</a>',
                obj.pk,
                count
            )
        return format_html('<span style="color:#9ca3af;">0 events</span>')

    @display(description=_('Friends'), ordering='friendships_count')
    def friends_count(self, obj):
        count = obj.friendships_count
        if count > 0:
            return format_html(
                '<a href="/admin/friendships/friendship/?q={}" style="color:#8b5cf6;font-weight:500;">{} friends</a>',
                obj.email,
                count
            )
        return format_html('<span style="color:#9ca3af;">0 friends</span>')

    @display(description=_('Joined'), ordering='created_at')
    def joined_date(self, obj):
        """Display formatted creation date."""
        return obj.created_at.strftime('%b %d, %Y')

    @display(description=_('User Statistics'))
    def user_statistics(self, obj):
        """Display comprehensive user statistics."""
        if not obj.pk:
            return "Save user to see statistics"
        
        stats_html = f"""
        <div style="padding:15px;background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;">
            <h3 style="margin:0 0 15px 0;color:#374151;font-size:14px;">User Activity Overview</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Organized Events:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.organized_events.count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Event Participations:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.event_participations.count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Friendships:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.sent_friendships.filter(status='accepted').count() + obj.received_friendships.filter(status='accepted').count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Comments Posted:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.comments.count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Photos Uploaded:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.uploaded_photos.count()}</td>
                </tr>
                <tr style="border-top:2px solid #e5e7eb;">
                    <td style="padding:8px 0;color:#6b7280;"><strong>Last Login:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.last_login.strftime('%b %d, %Y %H:%M') if obj.last_login else 'Never'}</td>
                </tr>
            </table>
        </div>
        """
        return format_html(stats_html)

    @admin.action(description=_('Activate selected users'))
    def activate_users(self, request, queryset):
        """Bulk activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')

    @admin.action(description=_('Deactivate selected users'))
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')

    @admin.action(description=_('Grant staff permissions'))
    def make_staff(self, request, queryset):
        """Grant staff permissions to users."""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users granted staff permissions.')

    @admin.action(description=_('Remove staff permissions'))
    def remove_staff(self, request, queryset):
        """Remove staff permissions from users."""
        updated = queryset.filter(is_superuser=False).update(is_staff=False)
        self.message_user(request, f'{updated} users had staff permissions removed.')