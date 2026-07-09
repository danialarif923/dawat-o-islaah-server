"""
Import merged hadith JSON files (Arabic + English + Urdu + chapters).

Usage:
  python manage.py import_merged --data=path/to/merged/ahmad.json
  python manage.py import_merged --data=path/to/merged/darmi.json
  python manage.py import_merged --all --dir=path/to/merged/
"""
import json, os
from django.core.management.base import BaseCommand
from django.db import transaction
from hadith.models import Hadith, Book


class Command(BaseCommand):
    help = "Import merged hadith data JSON files"

    def add_arguments(self, parser):
        parser.add_argument("--data", help="Path to a single merged JSON file")
        parser.add_argument("--all", action="store_true", help="Import all JSON files in --dir")
        parser.add_argument("--dir", default="merged_data", help="Directory with merged JSON files")

    def handle(self, *args, **options):
        if options["all"]:
            data_dir = options["dir"]
            for fname in sorted(os.listdir(data_dir)):
                if fname.endswith(".json"):
                    path = os.path.join(data_dir, fname)
                    self.import_file(path)
        elif options["data"]:
            self.import_file(options["data"])
        else:
            self.stderr.write("Provide --data or --all --dir")

    def import_file(self, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        book_name = data["book_name"]
        book_order = data["book_order"]
        hadiths = data["hadiths"]

        self.stdout.write(f"\nImporting {book_name} ({len(hadiths)} hadiths)...")

        with transaction.atomic():
            book_obj, _ = Book.objects.get_or_create(
                name=book_name,
                defaults={"order": book_order},
            )

            created = 0
            updated = 0
            for h in hadiths:
                _, was_created = Hadith.objects.update_or_create(
                    book=book_obj,
                    hadith_number=h["hadith_number"],
                    defaults={
                        "chapter_english": h.get("chapter_english", "") or "",
                        "chapter_arabic": h.get("chapter_arabic", "") or "",
                        "arabic_text": h.get("arabic_text", "") or "",
                        "english_text": h.get("english_text", "") or "",
                        "urdu_text": h.get("urdu_text", "") or "",
                        "reference": h.get("reference", "") or "",
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        with_arb = sum(1 for h in hadiths if h.get("arabic_text"))
        with_eng = sum(1 for h in hadiths if h.get("english_text"))
        with_urd = sum(1 for h in hadiths if h.get("urdu_text"))

        self.stdout.write(self.style.SUCCESS(
            f"  {created} created, {updated} updated | "
            f"arb={with_arb}, eng={with_eng}, urd={with_urd}"
        ))
