# Generated by Django 2.2.2 on 2019-06-21 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eyra_data', '0005_auto_20190614_1420'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='additional_data_files',
            new_name='participant_data_files',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='test_ground_truth_data_file',
            new_name='public_ground_truth_data_file',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='test_data_file',
            new_name='public_test_data_file',
        ),
        migrations.AddField(
            model_name='dataset',
            name='private_ground_truth_data_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='eyra_data.DataFile'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='private_test_data_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='eyra_data.DataFile'),
        ),
    ]
