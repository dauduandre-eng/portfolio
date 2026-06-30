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

    # Structured case-study fields, replacing the original single
    # freeform `description`. Each is independently optional: a small
    # weekend project might only ever have "solution" filled in, and the
    # template only renders a section heading when that field actually
    # has content - never an empty "Lessons Learned" header floating over
    # nothing. This is the literal mechanism that makes a project read as
    # a deliberate case study instead of a screenshot with a caption.
    problem = models.TextField(
        blank=True, help_text="What problem was this solving, and for whom?"
    )
    solution = models.TextField(
        blank=True, help_text="What did you actually build, and how?"
    )
    challenges = models.TextField(
        blank=True, help_text="What was genuinely hard about it, and why?"
    )
    outcome = models.TextField(
        blank=True, help_text="What happened once it was built or shipped?"
    )
    lessons_learned = models.TextField(
        blank=True, help_text="What would you do differently next time?"
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
