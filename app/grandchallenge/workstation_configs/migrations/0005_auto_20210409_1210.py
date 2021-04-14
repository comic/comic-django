# Generated by Django 3.1.8 on 2021-04-09 12:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workstation_configs", "0004_workstationconfig_overlay_luts"),
    ]

    operations = [
        migrations.AddField(
            model_name="windowpreset",
            name="lower_percentile",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(limit_value=100)
                ],
            ),
        ),
        migrations.AddField(
            model_name="windowpreset",
            name="upper_percentile",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(limit_value=100)
                ],
            ),
        ),
        migrations.AlterField(
            model_name="windowpreset",
            name="center",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="windowpreset",
            name="width",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(limit_value=1)
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="windowpreset",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("center__isnull", False),
                        ("lower_percentile__isnull", True),
                        ("upper_percentile__isnull", True),
                        ("width__isnull", False),
                    ),
                    models.Q(
                        ("center__isnull", True),
                        ("lower_percentile__isnull", False),
                        ("upper_percentile__isnull", False),
                        ("width__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="workstation_configs_windowpreset_either_fixed_or_percentile",
            ),
        ),
        migrations.AddConstraint(
            model_name="windowpreset",
            constraint=models.CheckConstraint(
                check=models.Q(
                    upper_percentile__gt=django.db.models.expressions.F(
                        "lower_percentile"
                    )
                ),
                name="workstation_configs_windowpreset_upper_gt_lower_percentile",
            ),
        ),
        migrations.AddConstraint(
            model_name="windowpreset",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("width__gt", 0), ("width__isnull", True), _connector="OR"
                ),
                name="workstation_configs_windowpreset_width_gt_0",
            ),
        ),
    ]
