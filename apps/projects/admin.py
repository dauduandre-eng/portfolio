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
    search_fields = ["title", "summary", "problem", "solution"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["technologies"]

    # Grouped into a fieldset so the five case-study fields read as a
    # deliberate structure in admin, not a flat scroll of textareas with
    # no indication of which goes where.
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary")}),
        (
            "Case study",
            {
                "fields": (
                    "problem",
                    "solution",
                    "challenges",
                    "outcome",
                    "lessons_learned",
                ),
                "description": "All optional - leave a field blank and its "
                "section simply doesn't appear on the live page.",
            },
        ),
        (
            "Links & technologies",
            {"fields": ("technologies", "github_url", "live_url", "image_url")},
        ),
        ("Publishing", {"fields": ("is_published", "display_order")}),
    )
