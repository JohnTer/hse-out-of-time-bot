# Generated by Django 3.1 on 2020-08-27 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_auto_20200827_0349'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='solving_mode',
            field=models.BooleanField(default=False),
        ),
    ]
