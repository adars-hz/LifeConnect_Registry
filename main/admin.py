from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from .models import User, DonorProfile, RecipientProfile, Document, VerificationRequest, Message, ActivityLog

# Register only User model to avoid recursion issues
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'verification_status', 'is_verified', 'created_at')
    list_filter = ('user_type', 'verification_status', 'is_verified', 'created_at')
    search_fields = ('username', 'email')
    list_editable = ('email', 'user_type', 'verification_status', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        # ONLY show users who completed FULL donor or recipient registration forms
        # Users must have DonorProfile or RecipientProfile (created only through registration forms)
        # Modal sign-ups (user_type='user') don't get profiles created by the signal
        # Exclude admin users and normal users from the user management section
        return super().get_queryset(request).filter(
            Q(donor_profile__isnull=False) | Q(recipient_profile__isnull=False)
        ).exclude(user_type__in=['admin', 'user'])
    
    def get_user_type_display(self, obj):
        color_map = {
            'donor': 'green',
            'recipient': 'blue',
            'admin': 'red',
        }
        color = color_map.get(obj.user_type, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_user_type_display())


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'uploaded_at', 'is_verified')
    list_filter = ('document_type', 'is_verified', 'uploaded_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('uploaded_at',)
    
    def get_queryset(self, request):
        # Only show documents for donor/recipient users, exclude admin and normal users
        return super().get_queryset(request).filter(
            Q(user__donor_profile__isnull=False) | Q(user__recipient_profile__isnull=False)
        ).exclude(user__user_type__in=['admin', 'user'])
    
    def get_user_display(self, obj):
        return f"{obj.user.username} ({obj.user.email})"


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('request_type', 'status', 'created_at', 'reviewed_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        # Only show verification requests for donor/recipient users, exclude admin and normal users
        return super().get_queryset(request).filter(
            Q(user__donor_profile__isnull=False) | Q(user__recipient_profile__isnull=False)
        ).exclude(user__user_type__in=['admin', 'user'])
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'request_type', 'status')
        }),
        ('Admin Actions', {
            'fields': ('admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'message_type', 'is_read', 'is_important', 'sent_at')
    list_filter = ('message_type', 'is_read', 'is_important', 'sent_at')
    search_fields = ('user__username', 'user__email', 'subject')
    readonly_fields = ('sent_at', 'read_at')
    
    def get_queryset(self, request):
        # Only show messages for donor/recipient users, exclude admin and normal users
        return super().get_queryset(request).filter(
            Q(user__donor_profile__isnull=False) | Q(user__recipient_profile__isnull=False)
        ).exclude(user__user_type__in=['admin', 'user'])
    
    fieldsets = (
        ('Message Information', {
            'fields': ('user', 'subject', 'message_type', 'content')
        }),
        ('Status', {
            'fields': ('is_read', 'is_important')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'read_at')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'activity_type')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        # Only show activity logs for donor/recipient users, exclude admin and normal users
        return super().get_queryset(request).filter(
            Q(user__donor_profile__isnull=False) | Q(user__recipient_profile__isnull=False)
        ).exclude(user__user_type__in=['admin', 'user'])
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
