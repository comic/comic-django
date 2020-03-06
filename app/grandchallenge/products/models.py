from django.db import models
from django.utils import timezone

from grandchallenge.challenges.models import get_logo_path


class Company(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=timezone.now)
    company_name = models.CharField(max_length=200)
    website = models.URLField()
    founded = models.IntegerField()
    hq = models.CharField(max_length=100)
    email = models.EmailField()
    logo = models.ImageField(upload_to=get_logo_path, null=True,)
    description = models.TextField(
        blank=True, help_text="Short summary of this project.",
    )
    description_short = models.CharField(
        max_length=250,
        blank=True,
        help_text="Short summary of this project, max 250 characters.",
    )

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "companies"


class ProductImage(models.Model):
    img = models.ImageField(upload_to=get_logo_path)


class Status(object):
    CERTIFIED = "cer"
    YES = "yes"
    NO = "no"
    NA = "na"
    CLEARED = "cle"
    DE_NOVO_CLEARED = "dnc"
    PMA_APPROVED = "pma"
    UNKNOWN = "unk"


class Product(models.Model):
    class Verified(models.TextChoices):
        YES = Status.YES, "Yes"
        NO = Status.NO, "No"

    class CEStatus(models.TextChoices):
        CERTIFIED = Status.CERTIFIED, "Certified"
        NO = Status.NO, "No or not yet"
        NA = Status.NA, "Not applicable"
        UNKNOWN = Status.UNKNOWN, "Unknown"

    class FDAStatus(models.TextChoices):
        CLEARED = Status.CLEARED, "510(k) cleared"
        DE_NOVO_CLEARED = Status.DE_NOVO_CLEARED, "De novo 510(k) cleared"
        PMA_APPROVED = Status.PMA_APPROVED, "PMA approved"
        NO = Status.NO, "No or not yet"
        NA = Status.NA, "Not applicable"
        UNKNOWN = Status.UNKNOWN, "Unknown"

    ICONS = {
        Status.CERTIFIED: "icon_check.png",
        Status.YES: "icon_check.png",
        Status.NO: "icon_no.png",
        Status.NA: "icon_na.png",
        Status.CLEARED: "icon_check.png",
        Status.DE_NOVO_CLEARED: "icon_check.png",
        Status.PMA_APPROVED: "icon_check.png",
        Status.UNKNOWN: "icon_question.png",
    }

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=timezone.now)
    product_name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    short_name = models.CharField(
        max_length=500,
        blank=False,
        help_text=(
            "short name used in url, specific css, files etc. No spaces allowed"
        ),
        unique=True,
    )
    description = models.TextField(
        blank=True, help_text="Short summary of this project.",
    )
    description_short = models.CharField(
        max_length=250,
        default="",
        blank=True,
        help_text="Short summary of this project, max 250 characters.",
    )
    modality = models.CharField(max_length=100)
    subspeciality = models.CharField(max_length=300)
    diseases = models.TextField()
    population = models.TextField()

    input_data = models.CharField(max_length=150)
    file_format_input = models.TextField()
    output_data = models.CharField(max_length=150)
    file_format_output = models.TextField()
    key_features = models.TextField()
    key_features_short = models.CharField(max_length=120)
    software_usage = models.TextField()

    verified = models.CharField(
        choices=Verified.choices, max_length=3, default=Verified.NO
    )
    ce_status = models.CharField(
        choices=CEStatus.choices, max_length=3, default=CEStatus.NO
    )
    ce_class = models.CharField(max_length=500, default="unknown")
    fda_status = models.CharField(
        choices=FDAStatus.choices, max_length=3, default=FDAStatus.UNKNOWN
    )
    fda_class = models.CharField(max_length=500, default="unknown")
    ce_verified = models.CharField(
        choices=Verified.choices, max_length=3, default=Verified.NO
    )

    integration = models.TextField()
    deployment = models.TextField()
    process_time = models.TextField()
    trigger = models.CharField(max_length=100)

    market_since = models.TextField()
    countries = models.TextField()
    distribution = models.CharField(max_length=100, blank=True)
    institutes_research = models.TextField()
    institutes_clinical = models.TextField()

    pricing_model = models.TextField()
    pricing_basis = models.TextField()

    tech_papers = models.TextField()
    clin_papers = models.TextField()
    tech_peer_papers = models.TextField()
    tech_other_papers = models.TextField()
    all_other_papers = models.TextField()

    images = models.ManyToManyField(ProductImage)

    def __str__(self):
        return self.short_name
