from django.db import models


class ContactMessage(models.Model):
    """
    Every submission is saved here regardless of whether the email
    notification below succeeds. That matters: if the SMTP provider has a
    bad day, a genuine inquiry still isn't lost — it's sitting in admin
    either way.
    """

    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
