from django.core.management import call_command
from django.core.management.base import BaseCommand

from crops.models import CropCategory


class Command(BaseCommand):
    help = "Load default example data if the database is empty."

    def handle(self, *args, **options):
        if CropCategory.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists — skipping seed."))
            return

        call_command("loaddata", "default_data.json", verbosity=0)
        self.stdout.write(self.style.SUCCESS("Default example data loaded successfully."))
