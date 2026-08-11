from django.contrib import admin
from .models import ContactMessage, BlogPost


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_editable = ('is_read',)
    list_filter = ('is_read',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
