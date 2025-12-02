"""
Admin configuration for Event model with Unfold.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from import_export.admin import ImportExportModelAdmin

from .models import Event, EVENT_STATUS_CHOICES
from apps.participants.models import EventParticipant
from apps.comments.models import EventComment
from apps.media.models import EventPhoto


class EventParticipantInline(TabularInline):
    """Inline for event participants."""
    model = EventParticipant
    extra = 0
    fields = ['user', 'status', 'is_admin', 'invited_by', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'invited_by']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'invited_by')


class EventCommentInline(TabularInline):
    """Inline for event comments."""
    model = EventComment
    extra = 0
    fields = ['user', 'content', 'parent', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'parent']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


class EventPhotoInline(TabularInline):
    """Inline for event photos."""
    model = EventPhoto
    extra = 0
    fields = ['uploaded_by', 'url', 'caption', 'is_cover', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['uploaded_by']


class StatusFilter(admin.SimpleListFilter):
    """Custom filter for event status."""
    title = _('Event Status')
    parameter_name = 'custom_status'

    def lookups(self, request, model_admin):
        return (
            ('upcoming', _('Upcoming Events')),
            ('ongoing', _('Ongoing Events')),
            ('past', _('Past Events')),
            ('full', _('Full Events')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from django.db import models
        now = timezone.now()
        
        if self.value() == 'upcoming':
            return queryset.filter(date__gt=now, status='published')
        if self.value() == 'ongoing':
            return queryset.filter(date__lte=now, status='published')
        if self.value() == 'past':
            return queryset.filter(status='completed')
        if self.value() == 'full':
            return queryset.annotate(
                participants_count=Count('participants_rel', filter=Q(participants_rel__status='accepted'))
            ).filter(
                participants_count__gte=models.F('max_participants')
            ).exclude(max_participants__isnull=True)
        return queryset


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin, ModelAdmin):
    """Enhanced admin interface for Event model."""
    
    list_display = [
        'title_with_status',
        'organizer_link',
        'location_info',
        'event_date',
        'status_badge',
        'capacity_info',
        'participants_count_display',
        'categories_display',
    ]
    
    list_filter = [
        StatusFilter,
        'status',
        ('date', RangeDateTimeFilter),
        ('country', RelatedDropdownFilter),
        ('city', RelatedDropdownFilter),
        'invitation_perm',
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'title',
        'description',
        'address',
        'organizer__email',
        'organizer__name',
    ]
    
    ordering = ['-date']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'event_statistics',
        'participants_list',
    ]
    
    autocomplete_fields = [
        'organizer',
        'country',
        'city',
    ]
    
    fieldsets = (
        (_('Event Information'), {
            'fields': ('title', 'description', 'organizer'),
            'description': 'Basic event information and organization',
        }),
        (_('Location'), {
            'fields': ('country', 'city', 'address'),
        }),
        (_('Schedule & Status'), {
            'fields': ('date', 'status'),
        }),
        (_('Settings'), {
            'fields': ('invitation_perm', 'max_participants'),
            'classes': ['collapse'],
        }),
        (_('Statistics'), {
            'fields': ('event_statistics', 'participants_list'),
            'classes': ['collapse'],
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )
    
    inlines = [EventParticipantInline, EventCommentInline, EventPhotoInline]
    
    actions = [
        'publish_events',
        'cancel_events',
        'complete_events',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'organizer', 'country', 'city'
        ).prefetch_related(
            'categories'
        ).annotate(
            participants_accepted=Count(
                'participants_rel',
                filter=Q(participants_rel__status='accepted'),
                distinct=True
            ),
            comments_count=Count('comments', distinct=True),
            photos_count=Count('photos', distinct=True),
        )

    # -------------------------------
    # Display methods - FIXED: Remove list wrapping
    # -------------------------------

    @display(description=_('Event'), ordering='title', header=True)
    def title_with_status(self, obj):
        from django.utils import timezone
        now = timezone.now()
        indicator = ''
        if obj.status == 'published':
            indicator = '<span style="color:#22c55e;">●</span> ' if obj.date > now else '<span style="color:#f59e0b;">●</span> '
        elif obj.status == 'cancelled':
            indicator = '<span style="color:#ef4444;">●</span> '
        # For header columns in Unfold, use mark_safe with list
        return [mark_safe(f'{indicator}<strong>{obj.title}</strong>')]

    @display(description=_('Organizer'), ordering='organizer__email')
    def organizer_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>', 
            obj.organizer.pk, 
            obj.organizer.name or obj.organizer.email
        )

    @display(description=_('Location'))
    def location_info(self, obj):
        parts = []
        if obj.city:
            parts.append(obj.city.name)
        if obj.country:
            parts.append(obj.country.name)
        if parts:
            return format_html('📍 {}', ', '.join(parts))
        return format_html('<span style="color:#9ca3af;">No location</span>')

    @display(description=_('Date & Time'), ordering='date')
    def event_date(self, obj):
        from django.utils import timezone
        now = timezone.now()
        color = '#22c55e' if obj.date > now else '#9ca3af'
        return format_html(
            '<span style="color:{};">{}</span>', 
            color, 
            obj.date.strftime('%b %d, %Y %H:%M')
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj):
        colors = {
            'draft': '#6b7280',
            'published': '#22c55e',
            'cancelled': '#ef4444',
            'completed': '#3b82f6'
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-size:11px;font-weight:500;">{}</span>', 
            colors.get(obj.status, '#6b7280'), 
            obj.get_status_display()
        )

    @display(description=_('Capacity'))
    def capacity_info(self, obj):
        if obj.max_participants:
            percentage = (obj.participants_accepted / obj.max_participants * 100)
            color = '#ef4444' if percentage >= 90 else '#f59e0b' if percentage >= 70 else '#22c55e'
            return format_html(
                '<span style="color:{};">{} / {}</span>', 
                color, 
                obj.participants_accepted, 
                obj.max_participants
            )
        return format_html('<span style="color:#6b7280;">Unlimited</span>')

    @display(description=_('Participants'), ordering='participants_accepted')
    def participants_count_display(self, obj):
        count = obj.participants_accepted
        if count > 0:
            return format_html(
                '<a href="/admin/participants/eventparticipant/?event__id__exact={}" style="color:#8b5cf6;font-weight:500;">{} participants</a>', 
                obj.pk, 
                count
            )
        return format_html('<span style="color:#9ca3af;">No participants</span>')

    @display(description=_('Categories'))
    def categories_display(self, obj):
        categories = obj.categories.all()[:3]
        if categories:
            badges = ''.join([
                f'<span style="background:#e0e7ff;color:#4f46e5;padding:2px 8px;border-radius:4px;font-size:10px;margin-right:4px;">{cat.name}</span>' 
                for cat in categories
            ])
            return format_html(badges)
        return format_html('<span style="color:#9ca3af;">No categories</span>')

    @display(description=_('Event Statistics'))
    def event_statistics(self, obj):
        """Display comprehensive event statistics."""
        if not obj.pk:
            return "Save event to see statistics"
        
        from django.utils import timezone
        now = timezone.now()
        days_until = (obj.date - now).days if obj.date > now else 0
        
        stats_html = f"""
        <div style="padding:15px;background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;">
            <h3 style="margin:0 0 15px 0;color:#374151;font-size:14px;">Event Overview</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Total Participants:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.participants_rel.count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Accepted:</strong></td>
                    <td style="text-align:right;color:#22c55e;font-weight:500;">{obj.participants_accepted}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Pending:</strong></td>
                    <td style="text-align:right;color:#f59e0b;">{obj.participants_rel.filter(status='pending').count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Admins:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.participants_rel.filter(is_admin=True).count()}</td>
                </tr>
                <tr style="border-top:1px solid #e5e7eb;">
                    <td style="padding:8px 0;color:#6b7280;"><strong>Comments:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.comments_count}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Photos:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.photos_count}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#6b7280;"><strong>Categories:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.categories.count()}</td>
                </tr>
                <tr style="border-top:2px solid #e5e7eb;">
                    <td style="padding:8px 0;color:#6b7280;"><strong>Days Until Event:</strong></td>
                    <td style="text-align:right;color:#8b5cf6;font-weight:600;">{days_until if days_until > 0 else 'Past Event'}</td>
                </tr>
            </table>
        </div>
        """
        return format_html(stats_html)

    @display(description=_('Participants List'))
    def participants_list(self, obj):
        """Display list of participants."""
        if not obj.pk:
            return "Save event to see participants"
        
        participants = obj.participants_rel.select_related('user').filter(
            status='accepted'
        )[:10]
        
        if not participants:
            return "No accepted participants yet"
        
        rows = ''.join([
            f'<tr><td style="padding:6px 0;">{p.user.name or p.user.email}</td><td style="text-align:right;"><span style="background:{"#3b82f6" if p.is_admin else "#e5e7eb"};color:{"white" if p.is_admin else "#374151"};padding:2px 8px;border-radius:4px;font-size:10px;">{"Admin" if p.is_admin else "Member"}</span></td></tr>'
            for p in participants
        ])
        
        html = f"""
        <div style="padding:15px;background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;">
            <table style="width:100%;">
                {rows}
            </table>
            {f'<p style="margin:10px 0 0 0;color:#6b7280;font-size:12px;">... and {obj.participants_accepted - 10} more</p>' if obj.participants_accepted > 10 else ''}
        </div>
        """
        return format_html(html)

    @admin.action(description=_('Publish selected events'))
    def publish_events(self, request, queryset):
        """Bulk publish events."""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} events published successfully.')

    @admin.action(description=_('Cancel selected events'))
    def cancel_events(self, request, queryset):
        """Bulk cancel events."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} events cancelled.')

    @admin.action(description=_('Mark as completed'))
    def complete_events(self, request, queryset):
        """Mark events as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} events marked as completed.')