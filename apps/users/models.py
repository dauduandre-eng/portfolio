from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model. Currently identical to Django's AbstractUser — this
    file is intentionally boring.

    Why it exists when it adds nothing yet: AUTH_USER_MODEL can only be
    changed before the first migration touches the auth app. Defining this
    now means any future field on the admin account (e.g. a short bio) is
    an ordinary migration later, instead of a project-wide data migration
    on a live database.
    """
