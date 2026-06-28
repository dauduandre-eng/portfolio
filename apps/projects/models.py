from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Technology(models.Model):
    """
    A single tag like "Django" or "PostgreSQL". A proper model + M2M
    relation instead of a comma-separated text field on Project — costs a
    few extra lines now, but guarantees "Django" is always spelled the
    same way everywhere, and leaves room for a tech-filtered project view
    later without a data migration.
    """

    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "technologies"

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        help_text="Auto-filled from the title if left blank. Changing it "
        "after publishing breaks any links already pointing at this page.",
    )
    summary = models.CharField(
        max_length=240,
        help_text="One or two sentences. Shown on the project list page.",
    )
    description = models.TextField(
        help_text="The full case study. Shown on the project detail page."
    )
    technologies = models.ManyToManyField(
        Technology, related_name="projects", blank=True
    )
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image_url = models.URLField(
        blank=True, help_text="Link to a hosted screenshot or preview image."
    )
    display_order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers appear first."
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to save a draft without it appearing on the live site.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
