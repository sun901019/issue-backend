from django.contrib import admin
from .models import (
    Issue, Project, Customer, Site, Asset,
    IssueStatusHistory, IssueComment, IssueAttachment,
    IssueSubtask, IssueRelation,
)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'assignee', 'reporter', 'created_at']
    list_filter = ['status', 'priority', 'category', 'source']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_person', 'contact_email']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'address']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'asset_code']


admin.site.register(IssueStatusHistory)
admin.site.register(IssueComment)
admin.site.register(IssueAttachment)
admin.site.register(IssueSubtask)
admin.site.register(IssueRelation)

