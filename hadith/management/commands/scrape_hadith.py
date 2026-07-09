import re
import time
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from hadith.models import Hadith, SyncStatus, Book, Chapter

BOOK_SLUG_MAP = {
    "ahmad": "musnad-ahmad",
    "darmi": "sunan-darimi",
    "malik": "muwatta-malik",
    "mustadrak": "mustadrak-al-hakim",
    "ibnkhuzaymah": "sahih-ibn-khuzaymah",
    "silsila-sahih": "al-silsila-sahiha",
}

BOOK_TOTALS = {
    "ahmad": 17360,
    "darmi": 3547,
    "malik": 1975,
    "mustadrak": 8803,
    "ibnkhuzaymah": 2414,
    "silsila-sahih": 4103,
}


class Command(BaseCommand):
    help = "Scrape Arabic + Urdu hadiths from al-hadees.com"

    def add_arguments(self, parser):
        parser.add_argument("--book", required=True,
                            help=f"Book slug: {', '.join(BOOK_SLUG_MAP.keys())}")
        parser.add_argument("--start", type=int, default=1,
                            help="Starting hadith number")
        parser.add_argument("--end", type=int, default=0,
                            help="Ending hadith number (default: auto-detect)")
        parser.add_argument("--delay", type=float, default=1.5,
                            help="Seconds between requests")
        parser.add_argument("--reset", action="store_true",
                            help="Reset progress and start from --start")

    def handle(self, *args, **options):
        slug = options["book"]
        delay = options["delay"]
        start = options["start"]

        if slug not in BOOK_SLUG_MAP:
            self.stderr.write(self.style.ERROR(f"Unknown book: {slug}"))
            self.stderr.write(f"Available: {', '.join(BOOK_SLUG_MAP.keys())}")
            return

        book_name = BOOK_SLUG_MAP[slug]
        end = options["end"] or BOOK_TOTALS.get(slug, 0)

        if end == 0:
            self.stderr.write(self.style.ERROR("Unknown total, specify --end"))
            return

        book_obj, created = Book.objects.get_or_create(
            name=book_name, defaults={"order": 0}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created book: {book_name}"))

        sync_name = f"scrape_{slug}"
        sync_status, _ = SyncStatus.objects.get_or_create(
            name=sync_name, defaults={"last_page": start}
        )

        if options["reset"]:
            sync_status.last_page = start
            sync_status.save()

        current = sync_status.last_page
        if start > current:
            current = start

        total = end - start + 1
        self.stdout.write(f"Scraping {book_name} ({slug}) #{current} - #{end} ({total} total)")

        done = 0
        skip = 0
        error = 0

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

        for num in range(current, end + 1):
            url = f"https://al-hadees.com/{slug}/{num}"

            try:
                resp = session.get(url, timeout=30)
                if resp.status_code == 404:
                    self.stdout.write(f"  #{num}: 404 - likely end of book, stopping")
                    break
                if resp.status_code != 200:
                    self.stdout.write(self.style.WARNING(f"  #{num}: HTTP {resp.status_code} - retrying once"))
                    time.sleep(delay * 2)
                    try:
                        resp = session.get(url, timeout=30)
                    except:
                        pass
                    if resp.status_code != 200:
                        error += 1
                        sync_status.last_page = num + 1
                        sync_status.save()
                        continue
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  #{num}: {e}"))
                error += 1
                time.sleep(delay * 3)
                sync_status.last_page = num
                sync_status.save()
                continue

            html = resp.text

            if len(html) < 1000:
                skip += 1
                sync_status.last_page = num + 1
                sync_status.save()
                continue

            arabic_text = self._extract_textarea(html, "content-arb-1")
            urdu_text = self._extract_textarea(html, "content-urd-1")

            if not arabic_text and not urdu_text:
                skip += 1
                sync_status.last_page = num + 1
                sync_status.save()
                continue

            chapter_name = self._extract_chapter(html)
            grade = self._extract_grade(html)

            if chapter_name:
                chapter = Chapter.objects.filter(book=book_obj, chapter_urdu=chapter_name).first()
                if chapter:
                    ch_num = chapter.chapter_number
                    ch_en = chapter.chapter_english or chapter_name
                    ch_ar = chapter.chapter_arabic or chapter_name
                    ch_ur = chapter.chapter_urdu or chapter_name
                else:
                    max_ch = Chapter.objects.filter(book=book_obj).aggregate(
                        m=Max("chapter_number")
                    )["m"]
                    ch_num = (max_ch or 0) + 1
                    chapter = Chapter.objects.create(
                        book=book_obj,
                        chapter_number=ch_num,
                        chapter_english=chapter_name,
                        chapter_arabic=chapter_name,
                        chapter_urdu=chapter_name,
                    )
                    ch_en = ch_ar = ch_ur = chapter_name
            else:
                ch_num = 0
                ch_en = ch_ar = ch_ur = ""

            Hadith.objects.update_or_create(
                book=book_obj,
                hadith_number=num,
                defaults={
                    "chapter_number": ch_num,
                    "chapter_english": ch_en,
                    "chapter_arabic": ch_ar,
                    "chapter_urdu": ch_ur,
                    "arabic_text": arabic_text,
                    "urdu_text": urdu_text,
                    "status": grade or "",
                    "reference": f"{book_name} #{num}",
                }
            )

            done += 1

            if done % 50 == 0:
                self.stdout.write(f"  [{done}/{total}] #{num} done, skips={skip}, errs={error}")

            sync_status.last_page = num + 1
            sync_status.save()

            time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Success: {done}, Skipped: {skip}, Errors: {error}"
        ))

    def _extract_textarea(self, html, textarea_id):
        match = re.search(
            rf'<textarea[^>]*id="{re.escape(textarea_id)}"[^>]*>(.*?)</textarea>',
            html, re.DOTALL
        )
        if not match:
            return ""
        text = match.group(1)
        text = text.replace("&#13;&#10;", "\n")
        text = text.replace("&#10;", "\n")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&#039;", "'")
        text = text.replace("&quot;", '"')
        return text.strip()

    def _extract_chapter(self, html):
        patterns = [
            r'<h[1-3][^>]*>(.*?)</h[1-3]>',
        ]
        for pat in patterns:
            matches = re.findall(pat, html, re.DOTALL)
            for m in matches:
                text = re.sub(r'<[^>]+>', '', m).strip()
                text = re.sub(r'\s+', ' ', text)
                if text and len(text) < 150 and any('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' for c in text):
                    return text
        return ""

    def _extract_grade(self, html):
        if "Sahih" in html or "صحيح" in html:
            return "Sahih"
        if "Hasan" in html or "حسن" in html:
            return "Hasan"
        if "Da'if" in html or "Daif" in html or "ضعيف" in html:
            return "Daif"
        return ""
