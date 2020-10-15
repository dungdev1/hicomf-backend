# Generated by Django 3.1.2 on 2020-10-15 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mains', '0009_auto_20201014_0650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='privacy',
        ),
        migrations.RemoveField(
            model_name='job',
            name='user',
        ),
        migrations.AddField(
            model_name='job',
            name='profile',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='mains.profile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='district',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='address',
            name='house_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=12),
        ),
        migrations.AlterField(
            model_name='profile',
            name='relationship',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
