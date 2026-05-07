from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("equipments", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipment",
            name="photo_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
