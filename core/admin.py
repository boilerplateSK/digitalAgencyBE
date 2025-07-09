# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Testimonial, ContactSubmission

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_company', 'rating', 'is_featured', 'is_active', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_active', 'created_at']
    search_fields = ['client_name', 'client_company', 'testimonial_text']
    list_editable = ['is_featured', 'is_active']
    ordering = ['-is_featured', '-created_at']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'client_company', 'client_position', 'client_image')
        }),
        ('Testimonial', {
            'fields': ('testimonial_text', 'rating')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'status', 'created_at', 'message_preview']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    list_editable = ['status']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message', 'status')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_preview.short_description = 'Message Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    actions = ['mark_as_replied', 'mark_as_closed']
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='replied')
        self.message_user(request, f'{updated} submissions marked as replied.')
    mark_as_replied.short_description = 'Mark selected submissions as replied'
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} submissions marked as closed.')
    mark_as_closed.short_description = 'Mark selected submissions as closed'