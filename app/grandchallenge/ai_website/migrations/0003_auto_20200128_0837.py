# Generated by Django 2.2.9 on 2020-01-28 08:37

from django.db import migrations, models
import grandchallenge.ai_website.models
import grandchallenge.core.storage


class Migration(migrations.Migration):

    dependencies = [
        ('ai_website', '0002_auto_20191210_0937'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, default='', upload_to='media/product_images/')),
            ],
        ),
        migrations.RemoveField(
            model_name='companyentry',
            name='published_date',
        ),
        migrations.AddField(
            model_name='companyentry',
            name='description_short',
            field=models.CharField(blank=True, help_text='Short summary of this project, max 250 characters.', max_length=250),
        ),
        migrations.AddField(
            model_name='companyentry',
            name='logo',
            field=models.ImageField(blank=True, storage=grandchallenge.core.storage.PublicS3Storage(), upload_to=grandchallenge.ai_website.models.get_logo_path),
        ),
        migrations.AddField(
            model_name='productbasic',
            name='description_short',
            field=models.CharField(blank=True, help_text='Short summary of this project, max 250 characters.', max_length=250),
        ),
        migrations.AlterField(
            model_name='productbasic',
            name='description',
            field=models.CharField(blank=True, default='', help_text='Short summary of this project, max 300 characters.', max_length=300),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='ce_status',
            field=models.CharField(default='no', max_length=10),
        ),
    ]
