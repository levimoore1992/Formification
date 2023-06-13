# Generated by Django 3.1.4 on 2021-03-12 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("formulaic", "0003_auto_20201230_1406"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="promo_source",
            field=models.CharField(
                blank=True,
                help_text="Source passed through metadata variable promo_source",
                max_length=200,
                null=True,
            ),
        ),
    ]
