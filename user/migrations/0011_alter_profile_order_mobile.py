# Generated by Django 5.1.4 on 2025-01-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_profile_order_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='order_mobile',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
