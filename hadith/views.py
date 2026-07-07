from .models import Hadith, Book
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.core.paginator import Paginator
from django.db.models import Q, Count


@api_view(['GET'])
def fetch_hadith_from_api(request):
    book_name = request.GET.get("book")
    if not book_name:
        return Response({"error": "Book name is required"}, status=400)

    API_KEY = "$2y$10$d4nL2E660zHHBrwTB7Bviu3WvW5sToLRBWFbJ1yhn7rJzSuNpA0S"
    normalized_name = book_name.replace("-", " ").title()

    book_obj, _ = Book.objects.get_or_create(
        name=normalized_name,
        defaults={"order": 0}
    )

    created_count = 0
    page = 1

    while True:
        try:
            response = requests.get(
                "https://hadithapi.com/api/hadiths",
                params={"apiKey": API_KEY, "book": book_name, "page": page},
                timeout=30
            )
            data = response.json()
        except Exception:
            break

        hadiths_data = data.get("hadiths", {}).get("data", [])
        if not hadiths_data:
            break

        for h_data in hadiths_data:
            chapter_data = h_data.get("chapter", {})

            if isinstance(chapter_data, dict):
                chapter_english = chapter_data.get("chapterEnglish", "General")
                chapter_arabic = chapter_data.get("chapterArabic", "")
            else:
                chapter_english = chapter_data or "General"
                chapter_arabic = ""

            try:
                hadith_number = int(h_data.get("hadithNumber") or 0)
            except:
                continue

            _, created = Hadith.objects.get_or_create(
                book=book_obj,
                hadith_number=hadith_number,
                defaults={
                    "chapter_english": chapter_english,
                    "chapter_arabic": chapter_arabic,
                    "arabic_text": h_data.get("hadithArabic"),
                    "english_text": h_data.get("hadithEnglish"),
                    "reference": str(h_data.get("id") or ""),
                }
            )

            if created:
                created_count += 1

        page += 1

    return Response({"message": f"{created_count} hadiths added successfully."})


URDU_TRANSLATION_MAP = {
    "sunan-abu-dawood": "╪│┘å┘å ╪º╪¿┘ê ╪»╪º╪ñ╪»",
    "abu-dawood": "╪│┘å┘å ╪º╪¿┘ê ╪»╪º╪ñ╪»",
    "sahih-bukhari": "╪╡╪¡█î╪¡ ╪¿╪«╪º╪▒█î",
    "sahih-muslim": "╪╡╪¡█î╪¡ ┘à╪│┘ä┘à",
    "al-tirmidhi": "╪¼╪º┘à╪╣ ╪¬╪▒┘à╪░█î",
    "tirmidhi": "╪¼╪º┘à╪╣ ╪¬╪▒┘à╪░█î",
    "sunan-nasai": "╪│┘å┘å ┘å╪│╪º╪ª█î",
    "sunan-ibn-e-majah": "╪│┘å┘å ╪º╪¿┘å ┘à╪º╪¼█ü",
    "ibn-e-majah": "╪│┘å┘å ╪º╪¿┘å ┘à╪º╪¼█ü",
    "mishkat-al-masabih": "┘à╪┤┌⌐╪º█â ╪º┘ä┘à╪╡╪º╪¿█î╪¡",
    "mishkat": "┘à╪┤┌⌐╪º█â ╪º┘ä┘à╪╡╪º╪¿█î╪¡",
    "musnad-ahmad": "┘à╪│┘å╪» ╪º╪¡┘à╪»",
    "sunan-darimi": "╪│┘å┘å ╪»╪º╪▒┘à█î",
    "muwatta-malik": "┘à┘ê╪╖╪º ┘à╪º┘ä┌⌐",
    "mustadrak-al-hakim": "┘à╪│╪¬╪»╪▒┌⌐ ╪¡╪º┌⌐┘à",
    "sahih-ibn-khuzaymah": "╪╡╪¡█î╪¡ ╪º╪¿┘å ╪«╪▓█î┘à█ü",
}

DB_BOOK_NAME_MAP = {
    "abu-dawood": "Sunan Abu Dawood",
    "sunan-abu-dawood": "Sunan Abu Dawood",
    "tirmidhi": "Al Tirmidhi",
    "al-tirmidhi": "Al Tirmidhi",
    "mishkat": "Mishkat Al Masabih",
}


def _resolve_book(book_slug):
    if not book_slug:
        return None

    slug = book_slug.lower().strip()

    book = Book.objects.filter(name__iexact=slug).first()
    if book:
        return book

    db_name = DB_BOOK_NAME_MAP.get(slug)
    if db_name:
        book = Book.objects.filter(name__iexact=db_name).first()
        if book:
            return book

    title_name = slug.replace("-", " ").title()
    book = Book.objects.filter(name__iexact=title_name).first()
    if book:
        return book

    contains_name = slug.replace("-", " ")
    book = Book.objects.filter(name__icontains=contains_name).first()
    if book:
        return book

    return None


@api_view(["GET"])
def get_books(request):
    WRITER_DATA = {
        "sahih-bukhari": {"writer": "Imam Bukhari", "death": "256 AH"},
        "sahih-muslim": {"writer": "Imam Muslim", "death": "261 AH"},
        "al-tirmidhi": {"writer": "Imam Tirmidhi", "death": "279 AH"},
        "sunan-abu-dawood": {"writer": "Imam Abu Dawood", "death": "275 AH"},
        "sunan-ibn-e-majah": {"writer": "Imam Ibn Majah", "death": "273 AH"},
        "ibn-e-majah": {"writer": "Imam Ibn Majah", "death": "273 AH"},
        "sunan-nasai": {"writer": "Imam Nasai", "death": "303 AH"},
        "mishkat": {"writer": "Al-Baghawi", "death": "516 AH"},
        "musnad-ahmad": {"writer": "Imam Ahmad", "death": "241 AH"},
        "sunan-darimi": {"writer": "Imam Darimi", "death": "255 AH"},
        "muwatta-malik": {"writer": "Imam Malik", "death": "179 AH"},
        "mustadrak-al-hakim": {"writer": "Imam Hakim", "death": "405 AH"},
        "sahih-ibn-khuzaymah": {"writer": "Ibn Khuzaymah", "death": "311 AH"},
    }

    books = Book.objects.all().order_by("order")
    data = []

    for b in books:
        slug = b.name.lower().replace(" ", "-")
        info = WRITER_DATA.get(slug, {"writer": "Unknown", "death": "Unknown"})

        chapters_count = (
            b.hadiths.values("chapter_english")
            .distinct()
            .count()
        )

        data.append({
            "name": b.name,
            "slug": slug,
            "hadiths_count": b.hadiths.count(),
            "chapters_count": chapters_count,
            "writerName": info["writer"],
            "writerDeath": info["death"],
        })

    return Response({"status": 200, "books": data})


def get_chapters_by_book(request):
    book_id = request.GET.get("book_id")
    if not book_id:
        return JsonResponse([], safe=False)

    try:
        chapters = (
            Hadith.objects.filter(book_id=book_id)
            .exclude(chapter_english__isnull=True)
            .exclude(chapter_english="")
            .values_list("chapter_english", flat=True)
            .distinct()
        )
        return JsonResponse(list(chapters), safe=False)
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['GET'])
def get_had_chapters(request):
    book_slug = request.GET.get("book")
    name_variant = book_slug.replace("-", " ")

    book_obj = Book.objects.filter(
        Q(name__iexact=book_slug) | Q(name__iexact=name_variant)
    ).first()

    if not book_obj:
        return Response({"status": 404, "error": "Book not found"}, status=404)

    hadiths = Hadith.objects.filter(book=book_obj).order_by("hadith_number")

    seen = set()
    chapters_list = []
    index = 0

    for h in hadiths:
        key = (h.chapter_english, h.chapter_arabic)

        if key not in seen:
            seen.add(key)

            chapters_list.append({
                "id": index,
                "bookSlug": book_slug,
                "chapterNumber": index,
                "chapterEnglish": h.chapter_english,
                "chapterArabic": h.chapter_arabic or "",
                "chapterUrdu": ""
            })

            index += 1

    return Response({"status": 200, "chapters": chapters_list})


# Γ£à HADITH API (WITH SEARCH NAVIGATION SUPPORT)
@api_view(['GET'])
def get_hadith(request):
    book_slug = request.GET.get("book")
    chapter_no = request.GET.get("chapter")
    page = request.GET.get("page", 1)
    hadith_number_param = request.GET.get("hadith")

    book_obj = _resolve_book(book_slug)

    if not book_obj:
        return Response({"status": 404, "error": "Book not found"}, status=404)

    # Build ordered chapter list for index mapping
    all_hadiths = Hadith.objects.filter(book=book_obj).order_by("hadith_number")
    seen = []
    chapter_index_map = {}
    for hh in all_hadiths:
        if hh.chapter_english not in seen:
            seen.append(hh.chapter_english)
            chapter_index_map[hh.chapter_english] = len(seen) - 1

    # =========================================================
    # FIND HADITH BY NUMBER OR FETCH LIST
    # =========================================================
    if hadith_number_param:
        try:
            target_hadith = Hadith.objects.get(
                book=book_obj,
                hadith_number=int(hadith_number_param)
            )

            chapter_index = chapter_index_map.get(target_hadith.chapter_english, 0)

            return Response({
                "status": 200,
                "chapterNumber": chapter_index,
                "hadiths": {
                    "data": [{
                        "hadithNumber": target_hadith.hadith_number,
                        "hadithArabic": target_hadith.arabic_text,
                        "hadithEnglish": target_hadith.english_text,
                        "hadithUrdu": target_hadith.urdu_text or "",
                        "reference": target_hadith.reference,
                        "status": "Sahih",
                        "bookSlug": book_slug,
                        "chapter": {
                            "chapterNumber": chapter_index,
                            "chapterEnglish": target_hadith.chapter_english,
                            "chapterArabic": target_hadith.chapter_arabic
                        },
                        "headingEnglish": "",
                        "headingArabic": "",
                        "headingUrdu": ""
                    }],
                    "last_page": 1
                }
            })

        except Hadith.DoesNotExist:
            return Response(
                {"status": 404, "error": "Hadith not found"},
                status=404
            )

    # =========================================================
    # NORMAL FLOW (FETCH HADITH LIST)
    # =========================================================
    hadith_queryset = Hadith.objects.filter(book=book_obj).order_by("hadith_number")

    if chapter_no is not None:
        try:
            chapter_index = int(chapter_no)
            chapter_name = seen[chapter_index]
        except:
            chapter_name = None

        if chapter_name:
            hadith_queryset = hadith_queryset.filter(
                chapter_english=chapter_name
            )

    paginator = Paginator(hadith_queryset, 20)
    page_obj = paginator.get_page(page)

    hadith_data = []
    for h in page_obj:
        hadith_data.append({
            "hadithNumber": h.hadith_number,
            "hadithArabic": h.arabic_text,
            "hadithEnglish": h.english_text,
            "hadithUrdu": h.urdu_text or "",
            "reference": h.reference,
            "status": "Sahih",
            "bookSlug": book_slug,
            "chapter": {
                "chapterNumber": chapter_index_map.get(h.chapter_english, 0),
                "chapterEnglish": h.chapter_english,
                "chapterArabic": h.chapter_arabic
            },
            "headingEnglish": "",
            "headingArabic": "",
            "headingUrdu": ""
        })

    return Response({
        "status": 200,
        "hadiths": {
            "data": hadith_data,
            "last_page": paginator.num_pages
        }
    })


@api_view(['GET'])
def search_hadith(request):
    q = request.GET.get('q', '').strip()
    book_slug = request.GET.get('book', '').strip()
    grade = request.GET.get('grade', '').strip()
    page = request.GET.get('page', 1)

    if not q:
        return Response({'results': [], 'total': 0, 'page': 1, 'per_page': 20, 'total_pages': 0, 'book_counts': {}})

    query = Q(arabic_text__icontains=q) | Q(english_text__icontains=q) | Q(urdu_text__icontains=q)

    if book_slug:
        book_obj = _resolve_book(book_slug)
        if book_obj:
            query &= Q(book=book_obj)

    if grade:
        query &= Q(status__iexact=grade)

    queryset = Hadith.objects.filter(query).order_by('book__order', 'hadith_number')

    book_counts = {}
    for entry in queryset.values('book__name').annotate(count=Count('id')).order_by():
        slug = entry['book__name'].lower().replace(' ', '-')
        book_counts[slug] = entry['count']

    limited = queryset

    results = []
    for h in limited:
        results.append({
            'hadithNumber': h.hadith_number,
            'hadithArabic': h.arabic_text,
            'hadithEnglish': h.english_text,
            'hadithUrdu': h.urdu_text or '',
            'reference': h.reference,
            'grade': h.status or '',
            'book': {
                'bookSlug': h.book.name.lower().replace(' ', '-'),
                'bookName': h.book.name,
            },
            'chapter': {
                'chapterNumber': h.chapter_number,
                'chapterEnglish': h.chapter_english,
                'chapterArabic': h.chapter_arabic or '',
            },
        })

    return Response({
        'results': results,
        'total': len(results),
        'book_counts': book_counts,
    })
