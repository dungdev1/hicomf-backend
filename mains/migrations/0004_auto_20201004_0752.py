# Generated by Django 3.1.2 on 2020-10-04 07:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mains', '0003_auto_20201004_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendshiprequest',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
