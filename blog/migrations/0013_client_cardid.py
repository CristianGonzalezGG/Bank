# Generated by Django 5.1.1 on 2025-02-13 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_loan'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='cardId',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
