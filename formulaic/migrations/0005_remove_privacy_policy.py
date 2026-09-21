from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("formulaic", "0004_submission_promo_source"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="form",
            name="privacy_policy",
        ),
        migrations.DeleteModel(
            name="PrivacyPolicy",
        ),
    ]
