from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crops', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crop',
            name='growth_duration_days',
            field=models.IntegerField(help_text='Number of days from planting to harvest.'),
        ),
    ]
