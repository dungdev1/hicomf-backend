# Generated by Django 3.1.2 on 2020-10-14 06:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mains', '0008_auto_20201013_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.AddField(
            model_name='address',
            name='profile',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='mains.profile'),
            preserve_default=False,
        ),
    ]
