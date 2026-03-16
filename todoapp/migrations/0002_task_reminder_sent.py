from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("todoapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="reminder_sent",
            field=models.BooleanField(default=False),
        ),
    ]
