from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin

admin.sites.AdminSite.site_title = 'مدیران وبلاگ'
admin.sites.AdminSite.site_header = 'مدیران وبلاگ'
admin.sites.AdminSite.index_title = 'مدیریت دیتابیس و سایت'


class ImageInline(admin.StackedInline):
    model = Image
    extra = 0


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'created', 'status')
    ordering = ('-created', '-title')
    list_filter = ('status', 'created', ('publish', JDateFieldListFilter))
    search_fields = ('title', 'description')
    raw_id_fields = ('author',)
    date_hierarchy = 'created'
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status',)
    list_display_links = ('title', 'author')
    inlines = [ImageInline, CommentInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'subject', 'status')
    ordering = ('-status', '-name')
    list_filter = ('status', 'subject')
    search_fields = ('name', 'description')
    list_editable = ('status', 'subject')
    list_display_links = ('name', 'title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created', 'updated', 'active')
    ordering = ('-created', '-name')
    list_filter = (('created', JDateFieldListFilter), 'active', 'name')
    search_fields = ('name', 'description')
    list_editable = ('active',)
    list_display_links = ('name', 'post')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'post', 'created')
    search_fields = ('title', 'description', 'post')
    ordering = ('-created',)
    raw_id_fields = ('post',)
