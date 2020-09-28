from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from grandchallenge.core.forms import SaveFormInitMixin
from grandchallenge.verifications.models import Verification
from grandchallenge.verifications.tokens import (
    email_verification_token_generator,
)


class VerificationForm(SaveFormInitMixin, forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields["user"].queryset = get_user_model().objects.filter(
            pk=self.user.pk
        )
        self.fields["user"].initial = self.user
        self.fields["user"].widget = forms.HiddenInput()

        self.fields["email"].initial = self.user.email
        self.fields["email"].required = True
        self.fields[
            "email"
        ].help_text = (
            "Please provide your work, corporate or institutional email"
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = BaseUserManager.normalize_email(email)

        domain = email.split("@")[1].lower()

        if domain in settings.DISALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError(
                f"Email addresses hosted by {domain} cannot be used"
            )

        if (
            get_user_model()
            .objects.filter(email__iexact=email)
            .exclude(pk=self.user.pk)
            .exists()
            or Verification.objects.filter(email__iexact=email).exists()
        ):
            raise ValidationError("This email is already in use")

        return email

    def clean(self):
        try:
            if self.user.verification:
                raise ValidationError(
                    "You have already made a verification request"
                )
        except ObjectDoesNotExist:
            pass

    class Meta:
        model = Verification
        fields = ("user", "email")


class ConfirmEmailForm(SaveFormInitMixin, forms.Form):
    token = forms.CharField(help_text="Enter your email confirmation token")

    def __init__(self, *args, user, token, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["token"].initial = token
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        if not email_verification_token_generator.check_token(
            self.user, cleaned_data["token"]
        ):
            raise ValidationError("Token is invalid")
