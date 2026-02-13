import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from quran.models import Tafseer


class Command(BaseCommand):

    help = "Load Tafseer from JSON files"

    def handle(self, *args, **kwargs):

        folder = os.path.join(
            settings.BASE_DIR,
            "quran",
            "tafseer_data"
        )

        if not os.path.exists(folder):
            self.stdout.write(self.style.ERROR("Folder not found"))
            return

        total = 0

        for file_name in sorted(os.listdir(folder)):

            if not file_name.endswith(".json"):
                continue

            file_path = os.path.join(folder, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            surah_number = data.get("surah_number")
            
            tafseer_list = sorted(
                data.get("tafsir", []),
                key=lambda x: int(x.get("ayah", 0))
            )


            for item in tafseer_list:

                ayah = item.get("ayah")
                tafseer_text = item.get("tafsir")

                if not ayah or not tafseer_text:
                    continue

                Tafseer.objects.update_or_create(

                    surah=surah_number,
                    ayat_number=ayah,

                    defaults={
                        "text": tafseer_text,
                        "author": "Imported Tafseer",
                        "language": "ur",
                    }
                )

                total += 1

            self.stdout.write(
                self.style.SUCCESS(f"Loaded Surah {surah_number}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"Total Tafseer Loaded: {total}")
        )
