# Generated by Django 3.1 on 2020-08-30 08:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_auto_20200829_0451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='path_media_content',
            new_name='media_name',
        ),
    ]
