from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class BlogPost(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        help_text="Auto-filled from the title if left blank. Changing it "
        "after publishing breaks existing links and feed entries.",
    )
    excerpt = models.CharField(
        max_length=240,
        help_text="Shown on the post list page and used as the RSS description.",
    )
    body = models.TextField()
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to save a draft without it appearing on the "
        "site or in the RSS feed.",
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="Controls sort order and the date shown publicly. "
        "Editable — unlike created_at below, which is fixed the moment "
        "the row is created.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
