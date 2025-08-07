from django.contrib import admin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for the User model."""
    list_display = ('id', 'email', 'username', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_active', 'role')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'security_question', 'security_answer')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'role')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'role')
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('groups', 'user_permissions')