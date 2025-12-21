from typing import List, Optional

from django.contrib import admin
from django.db.models import Count, F, Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateTimeFilter, RelatedDropdownFilter
from unfold.decorators import display

from apps.comments.models import EventComment
from apps.media.models import EventPhoto
from apps.participants.models import EventParticipant

from .models import Event


EVENT_STATUS_DRAFT = 'draft'
EVENT_STATUS_PUBLISHED = 'published'
EVENT_STATUS_CANCELLED = 'cancelled'
EVENT_STATUS_COMPLETED = 'completed'

INVITATION_STATUS_PENDING = 'pending'
INVITATION_STATUS_ACCEPTED = 'accepted'
INVITATION_STATUS_REJECTED = 'rejected'

FILTER_VALUE_UPCOMING = 'upcoming'
FILTER_VALUE_ONGOING = 'ongoing'
FILTER_VALUE_PAST = 'past'
FILTER_VALUE_FULL = 'full'

ADMIN_URL_USER_CHANGE = '/admin/users/user/{}/change/'
ADMIN_URL_PARTICIPANTS = '/admin/participants/eventparticipant/?event__id__exact={}'
ADMIN_URL_INVITATIONS_PENDING = '/admin/invitations/eventinvitation/?event__id__exact={}&status__exact=pending'

COLOR_SUCCESS = '#22c55e'
COLOR_WARNING = '#f59e0b'
COLOR_DANGER = '#ef4444'
COLOR_INFO = '#3b82f6'
COLOR_PRIMARY = '#8b5cf6'
COLOR_GRAY = '#6b7280'
COLOR_GRAY_LIGHT = '#9ca3af'

CAPACITY_THRESHOLD_HIGH = 90
CAPACITY_THRESHOLD_MEDIUM = 70

PARTICIPANTS_PREVIEW_LIMIT = 10

DATE_FORMAT = '%b %d, %Y %H:%M'


class EventParticipantInline(TabularInline):
    """Inline for event participants (accepted members only)."""
    model = EventParticipant
    extra = 0
    fields = ['user', 'is_admin', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user']
    verbose_name = 'Participant'
    verbose_name_plural = 'Participants (Accepted Members)'
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[EventParticipant]:
        """
        Get queryset with related user.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            QuerySet: Optimized queryset.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')


class EventCommentInline(TabularInline):
    """Inline for event comments."""
    model = EventComment
    extra = 0
    fields = ['user', 'content', 'parent', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'parent']
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[EventComment]:
        """
        Get queryset with related user.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            QuerySet: Optimized queryset.
        """
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

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> List[tuple]:
        """
        Return filter options.
        
        Args:
            request: The HTTP request object.
            model_admin: The model admin instance.
            
        Returns:
            List[tuple]: Filter choices.
        """
        return (
            (FILTER_VALUE_UPCOMING, _('Upcoming Events')),
            (FILTER_VALUE_ONGOING, _('Ongoing Events')),
            (FILTER_VALUE_PAST, _('Past Events')),
            (FILTER_VALUE_FULL, _('Full Events')),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[Event]) -> Optional[QuerySet[Event]]:
        """
        Filter queryset based on selected value.
        
        Args:
            request: The HTTP request object.
            queryset: The base queryset.
            
        Returns:
            Optional[QuerySet[Event]]: Filtered queryset or None.
        """
        now = timezone.now()
        
        if self.value() == FILTER_VALUE_UPCOMING:
            return queryset.filter(date__gt=now, status=EVENT_STATUS_PUBLISHED)
        if self.value() == FILTER_VALUE_ONGOING:
            return queryset.filter(date__lte=now, status=EVENT_STATUS_PUBLISHED)
        if self.value() == FILTER_VALUE_PAST:
            return queryset.filter(status=EVENT_STATUS_COMPLETED)
        if self.value() == FILTER_VALUE_FULL:
            return queryset.annotate(
                participants_count=Count('participants_rel')
            ).filter(
                participants_count__gte=F('max_participants')
            ).exclude(max_participants__isnull=True)
        return queryset


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin, ModelAdmin):
    """Enhanced admin interface for Event model."""
    
    list_display = [
        'title_with_status',
        'organizer_link',
        'location_info',
        'address',
        'event_date',
        'status_badge',
        'capacity_info',
        'participants_count_display',
        'invitations_count_display',
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        """
        Get queryset with optimized relations and annotations.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            QuerySet: Optimized queryset with counts.
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'organizer', 'country', 'city'
        ).prefetch_related(
            'categories'
        ).annotate(
            participants_count=Count('participants_rel', distinct=True),
            invitations_pending=Count(
                'invitations',
                filter=Q(invitations__status=INVITATION_STATUS_PENDING),
                distinct=True
            ),
            comments_count=Count('comments', distinct=True),
            photos_count=Count('photos', distinct=True),
        )

    @display(description=_('Event'), ordering='title', header=True)
    def title_with_status(self, obj: Event) -> List[SafeString]:
        """
        Display event title with status indicator.
        
        Args:
            obj: Event instance.
            
        Returns:
            List[SafeString]: HTML formatted title with indicator.
        """
        now = timezone.now()
        indicator = ''
        if obj.status == EVENT_STATUS_PUBLISHED:
            indicator = f'<span style="color:{COLOR_SUCCESS};">●</span> ' if obj.date > now else f'<span style="color:{COLOR_WARNING};">●</span> '
        elif obj.status == EVENT_STATUS_CANCELLED:
            indicator = f'<span style="color:{COLOR_DANGER};">●</span> '
        return [mark_safe(f'{indicator}<strong>{obj.title}</strong>')]

    @display(description=_('Organizer'), ordering='organizer__email')
    def organizer_link(self, obj: Event) -> SafeString:
        """
        Display organizer as link to user admin page.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted link to organizer.
        """
        return format_html(
            '<a href="{}" style="color:{};">{}</a>',
            ADMIN_URL_USER_CHANGE.format(obj.organizer.pk),
            COLOR_PRIMARY,
            obj.organizer.name or obj.organizer.email
        )

    @display(description=_('Location'))
    def location_info(self, obj: Event) -> SafeString:
        """
        Display location information.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted location.
        """
        parts = []
        if obj.city:
            parts.append(obj.city.name)
        if obj.country:
            parts.append(obj.country.name)
        if parts:
            return format_html('📍 {}', ', '.join(parts))
        return format_html('<span style="color:{};">No location</span>', COLOR_GRAY_LIGHT)

    @display(description=_('Date & Time'), ordering='date')
    def event_date(self, obj: Event) -> SafeString:
        """
        Display event date with color coding.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted date.
        """
        now = timezone.now()
        color = COLOR_SUCCESS if obj.date > now else COLOR_GRAY_LIGHT
        return format_html(
            '<span style="color:{};">{}</span>',
            color,
            obj.date.strftime(DATE_FORMAT)
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj: Event) -> SafeString:
        """
        Display status as colored badge.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted status badge.
        """
        status_colors = {
            EVENT_STATUS_DRAFT: COLOR_GRAY,
            EVENT_STATUS_PUBLISHED: COLOR_SUCCESS,
            EVENT_STATUS_CANCELLED: COLOR_DANGER,
            EVENT_STATUS_COMPLETED: COLOR_INFO
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-size:11px;font-weight:500;">{}</span>',
            status_colors.get(obj.status, COLOR_GRAY),
            obj.get_status_display()
        )

    @display(description=_('Capacity'))
    def capacity_info(self, obj: Event) -> SafeString:
        """
        Display capacity information with color coding.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted capacity.
        """
        if obj.max_participants:
            percentage = (obj.participants_count / obj.max_participants * 100)
            color = COLOR_DANGER if percentage >= CAPACITY_THRESHOLD_HIGH else COLOR_WARNING if percentage >= CAPACITY_THRESHOLD_MEDIUM else COLOR_SUCCESS
            return format_html(
                '<span style="color:{};">{} / {}</span>',
                color,
                obj.participants_count,
                obj.max_participants
            )
        return format_html('<span style="color:{};">Unlimited</span>', COLOR_GRAY)

    @display(description=_('Participants'), ordering='participants_count')
    def participants_count_display(self, obj: Event) -> SafeString:
        """
        Display participants count with link.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted participants count.
        """
        count = obj.participants_count
        if count > 0:
            return format_html(
                '<a href="{}" style="color:{};font-weight:500;">👥 {} members</a>',
                ADMIN_URL_PARTICIPANTS.format(obj.pk),
                COLOR_PRIMARY,
                count
            )
        return format_html('<span style="color:{};">No participants</span>', COLOR_GRAY_LIGHT)

    @display(description=_('Invitations'))
    def invitations_count_display(self, obj: Event) -> SafeString:
        """
        Display pending invitations count with link.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted invitations count.
        """
        pending = obj.invitations_pending
        if pending > 0:
            return format_html(
                '<a href="{}" style="color:{};font-weight:500;">📨 {} pending</a>',
                ADMIN_URL_INVITATIONS_PENDING.format(obj.pk),
                COLOR_WARNING,
                pending
            )
        return format_html('<span style="color:{};">No pending</span>', COLOR_GRAY_LIGHT)

    @display(description=_('Categories'))
    def categories_display(self, obj: Event) -> SafeString:
        """
        Display categories as badges.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted categories.
        """
        categories = obj.categories.all()[:3]
        if categories:
            badges = ''.join([
                f'<span style="background:#e0e7ff;color:#4f46e5;padding:2px 8px;border-radius:4px;font-size:10px;margin-right:4px;">{cat.name}</span>'
                for cat in categories
            ])
            return format_html(badges)
        return format_html('<span style="color:{};">No categories</span>', COLOR_GRAY_LIGHT)

    @display(description=_('Event Statistics'))
    def event_statistics(self, obj: Event) -> SafeString:
        """
        Display comprehensive event statistics.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted statistics table.
        """
        if not obj.pk:
            return "Save event to see statistics"
        
        now = timezone.now()
        days_until = (obj.date - now).days if obj.date > now else 0
        
        stats_html = f"""
        <div style="padding:15px;background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;">
            <h3 style="margin:0 0 15px 0;color:#374151;font-size:14px;">Event Overview</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="border-bottom:2px solid #e5e7eb;">
                    <td colspan="2" style="padding:8px 0;color:{COLOR_GRAY};font-weight:600;">Participants</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Total Members:</strong></td>
                    <td style="text-align:right;color:{COLOR_SUCCESS};font-weight:500;">{obj.participants_count}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Admins:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.participants_rel.filter(is_admin=True).count()}</td>
                </tr>
                <tr style="border-bottom:2px solid #e5e7eb;">
                    <td colspan="2" style="padding:8px 0;color:{COLOR_GRAY};font-weight:600;">Invitations</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Pending:</strong></td>
                    <td style="text-align:right;color:{COLOR_WARNING};font-weight:500;">{obj.invitations.filter(status=INVITATION_STATUS_PENDING).count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Accepted:</strong></td>
                    <td style="text-align:right;color:{COLOR_SUCCESS};">{obj.invitations.filter(status=INVITATION_STATUS_ACCEPTED).count()}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Rejected:</strong></td>
                    <td style="text-align:right;color:{COLOR_DANGER};">{obj.invitations.filter(status=INVITATION_STATUS_REJECTED).count()}</td>
                </tr>
                <tr style="border-top:1px solid #e5e7eb;">
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Comments:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.comments_count}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Photos:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.photos_count}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Categories:</strong></td>
                    <td style="text-align:right;color:#111827;">{obj.categories.count()}</td>
                </tr>
                <tr style="border-top:2px solid #e5e7eb;">
                    <td style="padding:8px 0;color:{COLOR_GRAY};"><strong>Days Until Event:</strong></td>
                    <td style="text-align:right;color:{COLOR_PRIMARY};font-weight:600;">{days_until if days_until > 0 else 'Past Event'}</td>
                </tr>
            </table>
        </div>
        """
        return format_html(stats_html)

    @display(description=_('Participants List'))
    def participants_list(self, obj: Event) -> SafeString:
        """
        Display list of participants.
        
        Args:
            obj: Event instance.
            
        Returns:
            SafeString: HTML formatted participants list.
        """
        if not obj.pk:
            return "Save event to see participants"
        
        participants = obj.participants_rel.select_related('user')[:PARTICIPANTS_PREVIEW_LIMIT]
        
        if not participants:
            return "No participants yet"
        
        rows = ''.join([
            f'<tr><td style="padding:6px 0;">{p.user.name or p.user.email}</td><td style="text-align:right;"><span style="background:{COLOR_INFO if p.is_admin else "#e5e7eb"};color:{"white" if p.is_admin else "#374151"};padding:2px 8px;border-radius:4px;font-size:10px;">{"Admin" if p.is_admin else "Member"}</span></td></tr>'
            for p in participants
        ])
        
        html = f"""
        <div style="padding:15px;background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;">
            <table style="width:100%;">
                {rows}
            </table>
            {f'<p style="margin:10px 0 0 0;color:{COLOR_GRAY};font-size:12px;">... and {obj.participants_count - PARTICIPANTS_PREVIEW_LIMIT} more</p>' if obj.participants_count > PARTICIPANTS_PREVIEW_LIMIT else ''}
        </div>
        """
        return format_html(html)

    @admin.action(description=_('Publish selected events'))
    def publish_events(self, request: HttpRequest, queryset: QuerySet[Event]) -> None:
        """
        Bulk publish events.
        
        Args:
            request: The HTTP request object.
            queryset: Selected events queryset.
        """
        updated = queryset.update(status=EVENT_STATUS_PUBLISHED)
        self.message_user(request, f'{updated} events published successfully.')

    @admin.action(description=_('Cancel selected events'))
    def cancel_events(self, request: HttpRequest, queryset: QuerySet[Event]) -> None:
        """
        Bulk cancel events.
        
        Args:
            request: The HTTP request object.
            queryset: Selected events queryset.
        """
        updated = queryset.update(status=EVENT_STATUS_CANCELLED)
        self.message_user(request, f'{updated} events cancelled.')

    @admin.action(description=_('Mark as completed'))
    def complete_events(self, request: HttpRequest, queryset: QuerySet[Event]) -> None:
        """
        Mark events as completed.
        
        Args:
            request: The HTTP request object.
            queryset: Selected events queryset.
        """
        updated = queryset.update(status=EVENT_STATUS_COMPLETED)
        self.message_user(request, f'{updated} events marked as completed.')