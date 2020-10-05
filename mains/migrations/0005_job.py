# Generated by Django 3.1.2 on 2020-10-05 06:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mains', '0004_auto_20201004_0752'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('starting_month', models.IntegerField()),
                ('starting_year', models.IntegerField()),
                ('ending_month', models.IntegerField(blank=True, null=True)),
                ('ending_year', models.IntegerField(blank=True, null=True)),
                ('still_working', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
