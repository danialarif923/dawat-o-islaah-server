"""
Import Quran word → root morphology data from mustafa0x/quran-morphology.

Downloads quran-morphology.txt from GitHub, parses it, and populates WordRoot.

Usage:
  python manage.py import_word_roots
  python manage.py import_word_roots --file=local/path.txt
"""
import re
import json
import os
import urllib.request
from django.core.management.base import BaseCommand
from django.db import transaction
from quran.models import WordRoot


MORPHOLOGY_URL = (
    "https://raw.githubusercontent.com/mustafa0x/"
    "quran-morphology/master/quran-morphology.txt"
)


ROOT_RE = re.compile(r'(?:^|\|)ROOT:([^|]+)')
LEM_RE = re.compile(r'(?:^|\|)LEM:([^|]+)')


def parse_line(line):
    parts = line.split("\t")
    if len(parts) < 4:
        return None
    key = parts[0].strip()
    text = parts[1].strip()
    tags = parts[3].strip()

    m = ROOT_RE.search(tags)
    root = m.group(1) if m else ""

    m = LEM_RE.search(tags)
    lemma = m.group(1) if m else ""

    key_parts = key.split(":")
    if len(key_parts) < 3:
        return None
    try:
        surah = int(key_parts[0])
        ayah = int(key_parts[1])
        word_idx = int(key_parts[2])
    except ValueError:
        return None

    return {
        "surah": surah,
        "ayah": ayah,
        "word_index": word_idx,
        "root_arabic": root.strip(),
        "lemma_arabic": lemma.strip(),
        "word_text": text,
    }


class Command(BaseCommand):
    help = "Import Quran word→root morphology data"

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Local path to quran-morphology.txt")
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing WordRoot data first"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing WordRoot data...")
            WordRoot.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        if options["file"]:
            path = options["file"]
            self.stdout.write(f"Reading from local file: {path}")
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        else:
            self.stdout.write(f"Downloading from: {MORPHOLOGY_URL}")
            req = urllib.request.Request(
                MORPHOLOGY_URL,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read().decode("utf-8")
            lines = data.splitlines()

        self.stdout.write(f"Loaded {len(lines)} lines")

        word_map = {}
        parsed = 0
        skipped_no_root = 0
        for line in lines:
            if not line.strip() or line.startswith("#"):
                continue
            result = parse_line(line)
            if result is None:
                continue
            parsed += 1
            key = (result["surah"], result["ayah"], result["word_index"])
            if not result["root_arabic"]:
                skipped_no_root += 1
                continue
            if key not in word_map:
                word_map[key] = result
            else:
                existing = word_map[key]
                if not existing["root_arabic"] and result["root_arabic"]:
                    word_map[key] = result

        self.stdout.write(
            f"Parsed {parsed} word parts, "
            f"{skipped_no_root} skipped (no root), "
            f"{len(word_map)} unique words to import"
        )

        batch = []
        BATCH_SIZE = 2000
        created = 0
        for key, rec in word_map.items():
            batch.append(
                WordRoot(
                    surah=rec["surah"],
                    ayah=rec["ayah"],
                    word_index=rec["word_index"],
                    root_arabic=rec["root_arabic"],
                    lemma_arabic=rec["lemma_arabic"],
                )
            )
            if len(batch) >= BATCH_SIZE:
                with transaction.atomic():
                    WordRoot.objects.bulk_create(batch, ignore_conflicts=True)
                created += len(batch)
                self.stdout.write(f"  Imported {created}/{len(word_map)}...")
                batch = []

        if batch:
            with transaction.atomic():
                WordRoot.objects.bulk_create(batch, ignore_conflicts=True)
            created += len(batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Imported {created} word→root records."
            )
        )
