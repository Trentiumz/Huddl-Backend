# Generated by Django 5.0.2 on 2024-08-17 13:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('huddl', '0002_remove_user_google_authenticated_alter_user_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('admin', models.ManyToManyField(related_name='clubs_managing', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='clubs', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clubs_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
