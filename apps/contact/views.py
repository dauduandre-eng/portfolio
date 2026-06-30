import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactForm

logger = logging.getLogger(__name__)

RATE_LIMIT_MAX_SUBMISSIONS = 5
RATE_LIMIT_WINDOW_SECONDS = 60 * 60  # 1 hour

# requests.post's timeout has two parts: time to establish a connection,
# then time waiting for a response after that. 5s to connect is generous
# for an HTTPS API call; 10s to respond covers a slow moment without
# risking gunicorn's own 30s worker timeout killing the whole process the
# way the original unbounded SMTP call did.
RESEND_TIMEOUT_SECONDS = (5, 10)


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
        # /admin/ instead of my inbox.
        #
        # This calls Resend's HTTP API directly rather than Django's SMTP
        # email backend. Render's free tier blocks outbound traffic to
        # SMTP ports (25, 465, 587) entirely at the network level — not a
        # credentials problem, a platform-level block that no amount of
        # correct Gmail App Password setup can work around. The previous
        # SMTP attempt didn't even fail cleanly: it hung inside
        # socket.connect() until gunicorn's own worker timeout killed the
        # entire process. An HTTPS POST on port 443 is never blocked the
        # same way, and the explicit timeout below means a slow network
        # now fails into this except block in seconds, not by taking the
        # whole worker down with it.
        if not settings.RESEND_API_KEY:
            # Mirrors the old console-email-backend behavior: local dev
            # never needs a real API key, the message just gets logged.
            logger.info(
                "RESEND_API_KEY not set - skipping real send. Message from "
                "%s <%s>: %s",
                contact_message.name,
                contact_message.email,
                contact_message.message,
            )
            return

        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json={
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": [settings.CONTACT_RECIPIENT_EMAIL],
                    "reply_to": contact_message.email,
                    "subject": f"New portfolio contact from {contact_message.name}",
                    "text": contact_message.message,
                },
                timeout=RESEND_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
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

