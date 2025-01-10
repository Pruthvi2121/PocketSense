# Generated by Django 5.0.3 on 2025-01-10 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_rename_added_by_groupexpense_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='collected_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
