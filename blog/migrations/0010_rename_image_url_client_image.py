# Generated by Django 5.1.1 on 2024-09-30 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_remove_client_image_client_image_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='image_url',
            new_name='image',
        ),
    ]