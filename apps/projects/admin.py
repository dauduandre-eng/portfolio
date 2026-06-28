from django.contrib import admin

from .models import Project, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "is_published", "display_order", "updated_at"]
    list_editable = ["is_published", "display_order"]
    list_filter = ["is_published", "technologies"]
    search_fields = ["title", "summary"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["technologies"]
