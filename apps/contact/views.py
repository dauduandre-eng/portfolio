import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactForm

logger = logging.getLogger(__name__)

RATE_LIMIT_MAX_SUBMISSIONS = 5
RATE_LIMIT_WINDOW_SECONDS = 60 * 60  # 1 hour


class ContactView(FormView):
    template_name = "contact/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:contact")

    def form_valid(self, form):
        # Honeypot tripped: pretend success without saving or emailing
        # anything. Showing a bot an error just teaches it to adjust;
        # showing it "success" wastes its time chasing a dead end instead.
        if form.cleaned_data.get("website"):
            return super().form_valid(form)

        if self._is_rate_limited():
            form.add_error(
                None, "Too many messages sent recently. Please try again later."
            )
            return self.form_invalid(form)

        contact_message = form.save()
        self._send_notification_email(contact_message)
        self._record_submission()

        messages.success(
            self.request, "Thanks for reaching out — I'll get back to you soon."
        )
        return super().form_valid(form)

    def _send_notification_email(self, contact_message):
        # The message is already saved at this point, so a failure here
        # never loses the inquiry — it just means I find out about it from
        # /admin/ instead of my inbox. Logged, not raised, so a flaky SMTP
        # provider can't turn a successful submission into a 500 error for
        # the visitor who just contacted me.
        try:
            email = EmailMessage(
                subject=f"New portfolio contact from {contact_message.name}",
                body=contact_message.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT_EMAIL],
                reply_to=[contact_message.email],
            )
            email.send(fail_silently=False)
        except Exception:
            logger.exception(
                "Failed to send contact notification email for message id=%s",
                contact_message.pk,
            )

    def _client_ip(self):
        # REMOTE_ADDR is the direct connection's IP. Behind a reverse proxy
        # (which Render's platform is), this may need to come from an
        # X-Forwarded-For header instead — a deployment-specific detail
        # we'll wire up properly in Milestone 8, not guess at here.
        return self.request.META.get("REMOTE_ADDR", "unknown")

    def _rate_limit_key(self):
        return f"contact-throttle:{self._client_ip()}"

    def _is_rate_limited(self):
        return cache.get(self._rate_limit_key(), 0) >= RATE_LIMIT_MAX_SUBMISSIONS

    def _record_submission(self):
        key = self._rate_limit_key()
        cache.set(key, cache.get(key, 0) + 1, timeout=RATE_LIMIT_WINDOW_SECONDS)
