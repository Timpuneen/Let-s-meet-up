from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import display, action
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    """Admin panel for custom User model with Unfold and soft delete support"""
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ['email', 'name', 'is_active', 'is_staff', 'status_badge', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_deleted', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    actions = ['restore_selected', 'hard_delete_selected']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal information', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Status', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login', 'deleted_at']
    
    def get_queryset(self, request):
        """Show all users including soft-deleted ones in admin"""
        return User.all_objects.all()
    
    @display(description='Status', ordering='is_deleted')
    def status_badge(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Deleted</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
        )
    
    @action(description='Restore selected users')
    def restore_selected(self, request, queryset):
        """Restore soft-deleted users"""
        count = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                count += 1
        self.message_user(request, f'{count} user(s) restored successfully.')
    
    @action(description='Permanently delete selected users')
    def hard_delete_selected(self, request, queryset):
        """Permanently delete users from database"""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f'{count} user(s) permanently deleted.')