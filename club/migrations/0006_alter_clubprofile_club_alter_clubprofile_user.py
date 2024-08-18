# Generated by Django 5.0.2 on 2024-08-17 23:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_alter_activity_cost_alter_activity_description'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='clubprofile',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='club_profiles', to='club.club'),
        ),
        migrations.AlterField(
            model_name='clubprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='club_profiles', to=settings.AUTH_USER_MODEL),
        ),
    ]
