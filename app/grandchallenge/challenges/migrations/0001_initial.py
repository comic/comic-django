# Generated by Django 3.1.1 on 2020-12-02 13:08

import re

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import grandchallenge.challenges.models
import grandchallenge.core.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("anatomy", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("task_categories", "0001_initial"),
        ("modalities", "0001_initial"),
        ("forum", "0011_auto_20190627_2132"),
        ("publications", "0003_auto_20201001_0758"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChallengeSeries",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    django.contrib.postgres.fields.citext.CICharField(
                        max_length=64, unique=True
                    ),
                ),
                ("url", models.URLField(blank=True)),
            ],
            options={
                "verbose_name_plural": "Challenge Series",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="ExternalChallenge",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "short_name",
                    django.contrib.postgres.fields.citext.CICharField(
                        help_text="short name used in url, specific css, files etc. No spaces allowed",
                        max_length=50,
                        unique=True,
                        validators=[
                            grandchallenge.challenges.models.validate_nounderscores,
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-zA-Z0-9_]+\\Z"),
                                "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                                "invalid",
                            ),
                            grandchallenge.challenges.models.validate_short_name,
                        ],
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short summary of this project, max 1024 characters.",
                        max_length=1024,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The name of the challenge that is displayed on the All Challenges page. If this is blank the short name of the challenge will be used.",
                        max_length=64,
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="A logo for this challenge. Should be square with a resolution of 640x640 px or higher.",
                        storage=grandchallenge.core.storage.PublicS3Storage(),
                        upload_to=grandchallenge.challenges.models.get_logo_path,
                    ),
                ),
                (
                    "hidden",
                    models.BooleanField(
                        default=True,
                        help_text="Do not display this Project in any public overview",
                    ),
                ),
                (
                    "educational",
                    models.BooleanField(
                        default=False,
                        help_text="It is an educational challange",
                    ),
                ),
                (
                    "workshop_date",
                    models.DateField(
                        blank=True,
                        help_text="Date on which the workshop belonging to this project will be held",
                        null=True,
                    ),
                ),
                (
                    "event_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The name of the event the workshop will be held at",
                        max_length=1024,
                        null=True,
                    ),
                ),
                (
                    "event_url",
                    models.URLField(
                        blank=True,
                        help_text="Website of the event which will host the workshop",
                        null=True,
                    ),
                ),
                (
                    "data_license_agreement",
                    models.TextField(
                        blank=True,
                        help_text="What is the data license agreement for this challenge?",
                    ),
                ),
                (
                    "number_of_training_cases",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "number_of_test_cases",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "filter_classes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.citext.CICharField(
                            max_length=32
                        ),
                        default=list,
                        editable=False,
                        size=None,
                    ),
                ),
                (
                    "homepage",
                    models.URLField(
                        help_text="What is the homepage for this challenge?"
                    ),
                ),
                (
                    "data_stored",
                    models.BooleanField(
                        default=False,
                        help_text="Has the grand-challenge team stored the data?",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modalities",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What imaging modalities are used in this challenge?",
                        to="modalities.ImagingModality",
                    ),
                ),
                (
                    "publications",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Which publications are associated with this challenge?",
                        to="publications.Publication",
                    ),
                ),
                (
                    "series",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Which challenge series is this associated with?",
                        to="challenges.ChallengeSeries",
                    ),
                ),
                (
                    "structures",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What structures are used in this challenge?",
                        to="anatomy.BodyStructure",
                    ),
                ),
                (
                    "task_types",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What type of task is this challenge?",
                        to="task_categories.TaskType",
                    ),
                ),
            ],
            options={"ordering": ("pk",), "abstract": False},
        ),
        migrations.CreateModel(
            name="Challenge",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "short_name",
                    django.contrib.postgres.fields.citext.CICharField(
                        help_text="short name used in url, specific css, files etc. No spaces allowed",
                        max_length=50,
                        unique=True,
                        validators=[
                            grandchallenge.challenges.models.validate_nounderscores,
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-zA-Z0-9_]+\\Z"),
                                "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                                "invalid",
                            ),
                            grandchallenge.challenges.models.validate_short_name,
                        ],
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short summary of this project, max 1024 characters.",
                        max_length=1024,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The name of the challenge that is displayed on the All Challenges page. If this is blank the short name of the challenge will be used.",
                        max_length=64,
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="A logo for this challenge. Should be square with a resolution of 640x640 px or higher.",
                        storage=grandchallenge.core.storage.PublicS3Storage(),
                        upload_to=grandchallenge.challenges.models.get_logo_path,
                    ),
                ),
                (
                    "hidden",
                    models.BooleanField(
                        default=True,
                        help_text="Do not display this Project in any public overview",
                    ),
                ),
                (
                    "educational",
                    models.BooleanField(
                        default=False,
                        help_text="It is an educational challange",
                    ),
                ),
                (
                    "workshop_date",
                    models.DateField(
                        blank=True,
                        help_text="Date on which the workshop belonging to this project will be held",
                        null=True,
                    ),
                ),
                (
                    "event_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The name of the event the workshop will be held at",
                        max_length=1024,
                        null=True,
                    ),
                ),
                (
                    "event_url",
                    models.URLField(
                        blank=True,
                        help_text="Website of the event which will host the workshop",
                        null=True,
                    ),
                ),
                (
                    "data_license_agreement",
                    models.TextField(
                        blank=True,
                        help_text="What is the data license agreement for this challenge?",
                    ),
                ),
                (
                    "number_of_training_cases",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "number_of_test_cases",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "filter_classes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.citext.CICharField(
                            max_length=32
                        ),
                        default=list,
                        editable=False,
                        size=None,
                    ),
                ),
                (
                    "banner",
                    models.ImageField(
                        blank=True,
                        help_text="Image that gets displayed at the top of each page. Recommended resolution 2200x440 px.",
                        storage=grandchallenge.core.storage.PublicS3Storage(),
                        upload_to=grandchallenge.challenges.models.get_banner_path,
                    ),
                ),
                (
                    "disclaimer",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Optional text to show on each page in the project. For showing 'under construction' type messages",
                        max_length=2048,
                        null=True,
                    ),
                ),
                (
                    "require_participant_review",
                    models.BooleanField(
                        default=False,
                        help_text="If ticked, new participants need to be approved by project admins before they can access restricted pages. If not ticked, new users are allowed access immediately",
                    ),
                ),
                (
                    "use_registration_page",
                    models.BooleanField(
                        default=True,
                        help_text="If true, show a registration page on the challenge site.",
                    ),
                ),
                (
                    "registration_page_text",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="The text to use on the registration page, you could include a data usage agreement here. You can use HTML markup here.",
                    ),
                ),
                (
                    "use_evaluation",
                    models.BooleanField(
                        default=False,
                        help_text="If true, use the automated evaluation system. See the evaluation page created in the Challenge site.",
                    ),
                ),
                (
                    "use_teams",
                    models.BooleanField(
                        default=False,
                        help_text="If true, users are able to form teams to participate in this challenge together.",
                    ),
                ),
                (
                    "display_forum_link",
                    models.BooleanField(
                        default=False,
                        help_text="Display a link to the challenge forum in the nav bar.",
                    ),
                ),
                (
                    "cached_num_participants",
                    models.PositiveIntegerField(default=0, editable=False),
                ),
                (
                    "cached_num_results",
                    models.PositiveIntegerField(default=0, editable=False),
                ),
                (
                    "cached_latest_result",
                    models.DateTimeField(
                        blank=True, editable=False, null=True
                    ),
                ),
                (
                    "admins_group",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="admins_of_challenge",
                        to="auth.group",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "forum",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="forum.forum",
                    ),
                ),
                (
                    "modalities",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What imaging modalities are used in this challenge?",
                        to="modalities.ImagingModality",
                    ),
                ),
                (
                    "participants_group",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participants_of_challenge",
                        to="auth.group",
                    ),
                ),
                (
                    "publications",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Which publications are associated with this challenge?",
                        to="publications.Publication",
                    ),
                ),
                (
                    "series",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Which challenge series is this associated with?",
                        to="challenges.ChallengeSeries",
                    ),
                ),
                (
                    "structures",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What structures are used in this challenge?",
                        to="anatomy.BodyStructure",
                    ),
                ),
                (
                    "task_types",
                    models.ManyToManyField(
                        blank=True,
                        help_text="What type of task is this challenge?",
                        to="task_categories.TaskType",
                    ),
                ),
            ],
            options={
                "verbose_name": "challenge",
                "verbose_name_plural": "challenges",
                "ordering": ("pk",),
                "abstract": False,
            },
        ),
    ]