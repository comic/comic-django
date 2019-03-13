# Generated by Django 2.1.5 on 2019-03-13 10:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0009_auto_20190204_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worklist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('images', models.ManyToManyField(blank=True, related_name='worklist', to='cases.Image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorklistSet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='worklist',
            name='set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worklists.WorklistSet'),
        ),
        migrations.AlterUniqueTogether(
            name='worklist',
            unique_together={('title', 'set')},
        ),
    ]
