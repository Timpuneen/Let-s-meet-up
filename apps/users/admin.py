from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'is_staff', 'invitation_privacy', 'created_at']
    search_fields = ['email', 'name']
    list_filter = ['is_active', 'is_staff', 'invitation_privacy', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
    
    fieldsets = (
        ('Account', {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('name', 'invitation_privacy')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )