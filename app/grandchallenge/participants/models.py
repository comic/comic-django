from django.conf import settings
from django.db import models

from grandchallenge.challenges.models import Challenge


class RequestBase(models.Model):
    """
    When a user wants to join a project, admins have the option of reviewing
    each user before allowing or denying them. This class records the needed
    info for that.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="which user requested to participate?",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    PENDING = "PEND"
    ACCEPTED = "ACPT"
    REJECTED = "RJCT"
    REGISTRATION_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )
    status = models.CharField(
        max_length=4, choices=REGISTRATION_CHOICES, default=PENDING
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def status_to_string(self):
        status = (
            f"Your request to join {self.object_name}, "
            f"sent {self.format_date(self.created)}"
        )
        if self.status == self.PENDING:
            status += ", is awaiting review"
        elif self.status == self.ACCEPTED:
            status += ", was accepted at " + self.format_date(self.changed)
        elif self.status == self.REJECTED:
            status += ", was rejected at " + self.format_date(self.changed)
        return status

    @staticmethod
    def format_date(date):
        return date.strftime("%b %d, %Y at %H:%M")

    def user_affiliation(self):
        profile = self.user.user_profile
        return profile.institution + " - " + profile.department

    class Meta:
        abstract = True


class RegistrationRequest(RequestBase):
    """
    When a user wants to join a project, admins have the option of reviewing
    each user before allowing or denying them. This class records the needed
    info for that.
    """

    challenge = models.ForeignKey(
        Challenge,
        help_text="To which project does the user want to register?",
        on_delete=models.CASCADE,
    )

    @property
    def object_name(self):
        return self.challenge.short_name

    def __str__(self):
        return f"{self.challenge.short_name} registration request by user {self.user.username}"

    class Meta:
        unique_together = (("challenge", "user"),)
