# Generated by Django 3.1.4 on 2020-12-30 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("formulaic", "0002_add_default_to_field_enabled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="option",
            name="position",
            field=models.PositiveIntegerField(default=0, verbose_name="Position"),
        ),
        migrations.AlterField(
            model_name="optiongroup",
            name="position",
            field=models.PositiveIntegerField(default=0, verbose_name="Position"),
        ),
    ]
