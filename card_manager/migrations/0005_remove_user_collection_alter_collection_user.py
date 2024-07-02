# Generated by Django 5.0.6 on 2024-07-02 22:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card_manager', '0004_collection_collection_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='collection',
        ),
        migrations.AlterField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='card_manager.user'),
        ),
    ]
