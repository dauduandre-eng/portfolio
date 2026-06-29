(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("chat-toggle");
    const closeBtn = document.getElementById("chat-close");
    const panel = document.getElementById("chat-panel");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const messagesEl = document.getElementById("chat-messages");

    function setOpen(open) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
      if (open) {
        input.focus();
      }
    }

    toggle.addEventListener("click", function () {
      setOpen(panel.hidden);
    });
    closeBtn.addEventListener("click", function () {
      setOpen(false);
    });

    function appendMessage(role, text) {
      const el = document.createElement("p");
      el.className = "chat-widget__message chat-widget__message--" + role;
      el.textContent = text;
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    // Django's CSRF middleware checks for the token in an X-CSRFToken
    // header on AJAX requests - a different mechanism than the hidden
    // {% csrf_token %} input we used for the contact form, since this
    // request sends a JSON body, not a normal form post. The token
    // itself comes from the csrftoken cookie, which JS can read because
    // it isn't HttpOnly (Django's default).
    function getCsrfToken() {
      const match = document.cookie.match(/(^|;)\s*csrftoken\s*=\s*([^;]+)/);
      return match ? match[2] : "";
    }

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) {
        return;
      }

      appendMessage("user", text);
      input.value = "";
      input.disabled = true;

      try {
        const response = await fetch("/chat/ask/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ message: text }),
        });
        const data = await response.json();
        appendMessage("assistant", data.reply || data.error || "Sorry, something went wrong.");
      } catch (err) {
        appendMessage("assistant", "Sorry, I'm having trouble connecting right now.");
      } finally {
        input.disabled = false;
        input.focus();
      }
    });
  });
})();
