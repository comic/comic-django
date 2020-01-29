# Generated by Django 2.2.9 on 2020-01-29 10:51

from django.db import migrations, models
import grandchallenge.ai_website.models
import grandchallenge.core.storage


class Migration(migrations.Migration):

    dependencies = [
        ('ai_website', '0006_auto_20200128_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productentry',
            name='ce_status',
            field=models.CharField(choices=[('cer', 'Certified'), ('no', 'No or not yet'), ('na', 'Not applicable'), ('unk', 'Unknown')], default='no', max_length=3),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='fda_status',
            field=models.CharField(choices=[('cle', '510(k) cleared'), ('dnc', 'De novo 510(k) cleared'), ('pma', 'PMA approved'), ('no', 'No or not yet'), ('na', 'Not applicable'), ('unk', 'Unknown')], default='unknown', max_length=3),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='verified',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=3),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='img',
            field=models.ImageField(blank=True, storage=grandchallenge.core.storage.PublicS3Storage(), upload_to=grandchallenge.ai_website.models.get_images_path),
        ),
    ]