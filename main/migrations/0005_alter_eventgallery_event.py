# Generated by Django 5.0.4 on 2024-11-01 08:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_event_image_eventgallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventgallery',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_galleries', to='main.event'),
        ),
    ]