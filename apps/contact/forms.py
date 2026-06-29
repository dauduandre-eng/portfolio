from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: hidden from real visitors via CSS (see the template), but a
    # simple spam bot blindly filling every input will fill this too.
    # required=False so a legitimate submission never fails validation on
    # it — we check its value explicitly in the view instead, where we can
    # decide deliberately what "spam detected" should do (pretend success,
    # not show an error a bot could learn from).
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }
