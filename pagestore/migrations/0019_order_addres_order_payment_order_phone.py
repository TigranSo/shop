# Generated by Django 4.2.1 on 2023-10-09 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagestore', '0018_remove_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='addres',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
