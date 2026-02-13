import requests

from django.core.management.base import BaseCommand
from quran.models import Ayat


class Command(BaseCommand):

    help = "Load Quran from AlQuran API into database"

    def handle(self, *args, **kwargs):

        self.stdout.write("Fetching Quran from API...")

        BASE_URL = "https://api.alquran.cloud/v1"

        # Get all surahs with ayahs
        url = f"{BASE_URL}/quran/quran-uthmani"

        response = requests.get(url)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("API Failed"))
            return

        data = response.json()["data"]["surahs"]

        total = 0

        for surah in data:

            surah_number = surah["number"]

            for ayah in surah["ayahs"]:

                ayat_number = ayah["numberInSurah"]
                text = ayah["text"]

                Ayat.objects.update_or_create(
                    surah=surah_number,
                    ayat_number=ayat_number,
                    defaults={
                        "text": text
                    }
                )

                total += 1

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {total} ayahs successfully!")
        )
