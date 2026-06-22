import re
from django.db.models import Q, Count
from quran.models import Ayat, Translation
from hadith.models import Hadith, Book

EN_TRANSLATOR = 'Saheeh International'
UR_TRANSLATOR = 'احمد رضا خان'

BOOK_NAME_MAP = {
    'sahih-bukhari': 'Sahih Bukhari',
    'sahih-muslim': 'Sahih Muslim',
    'al-tirmidhi': 'Jami` at-Tirmidhi',
    'abu-dawood': 'Sunan Abi Dawood',
    'ibn-e-majah': 'Sunan Ibn Majah',
    'mishkat': 'Mishkat al-Masabih',
    'sunan-nasai': 'Sunan an-Nasai',
}


def _strip_html(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('\ufeff', '').replace('\u200b', '')
    return text.strip()


def _format_book_name(book):
    return BOOK_NAME_MAP.get(book.name, book.name.replace('-', ' ').title())


def get_daily_content(user):
    if not user.current_hadith_book_id:
        first_book = Book.objects.annotate(cnt=Count('hadiths')).filter(cnt__gt=0).order_by('order').first()
        first_hadith = Hadith.objects.filter(book=first_book).order_by('hadith_number').first()
        user.current_hadith_book = first_book
        user.current_hadith_number = first_hadith.hadith_number
        user.save(update_fields=['current_hadith_book', 'current_hadith_number'])

    verse_obj = Ayat.objects.get(surah=user.current_verse_surah, ayat_number=user.current_verse_ayah)
    hadith_obj = Hadith.objects.get(book=user.current_hadith_book, hadith_number=user.current_hadith_number)

    en_trans = Translation.objects.filter(
        surah=verse_obj.surah, ayat_number=verse_obj.ayat_number,
        language='en', author__name=EN_TRANSLATOR
    ).first()
    ur_trans = Translation.objects.filter(
        surah=verse_obj.surah, ayat_number=verse_obj.ayat_number,
        language='ur', author__name=UR_TRANSLATOR
    ).first()

    verse = {
        'arabic': _strip_html(verse_obj.text),
        'english': _strip_html(en_trans.text) if en_trans else '',
        'urdu': _strip_html(ur_trans.text) if ur_trans else '',
        'reference': f'Surah {verse_obj.surah}:{verse_obj.ayat_number}',
    }

    hadith = {
        'arabic': _strip_html(hadith_obj.arabic_text or ''),
        'english': _strip_html(hadith_obj.english_text or ''),
        'urdu': _strip_html(hadith_obj.urdu_text or ''),
        'reference': f'{_format_book_name(hadith_obj.book)} - Hadith {hadith_obj.hadith_number}',
    }

    return verse, hadith


def advance_daily_content(user):
    next_verse = Ayat.objects.filter(
        Q(surah=user.current_verse_surah, ayat_number__gt=user.current_verse_ayah) |
        Q(surah__gt=user.current_verse_surah)
    ).order_by('surah', 'ayat_number').first()

    if next_verse:
        user.current_verse_surah = next_verse.surah
        user.current_verse_ayah = next_verse.ayat_number
    else:
        user.current_verse_surah = 1
        user.current_verse_ayah = 1

    next_hadith = Hadith.objects.filter(
        book=user.current_hadith_book,
        hadith_number__gt=user.current_hadith_number
    ).order_by('hadith_number').first()

    if next_hadith:
        user.current_hadith_number = next_hadith.hadith_number
    else:
        next_book = Book.objects.annotate(cnt=Count('hadiths')).filter(
            cnt__gt=0, order__gt=user.current_hadith_book.order
        ).order_by('order').first()

        if next_book:
            user.current_hadith_book = next_book
            first_hadith = Hadith.objects.filter(book=next_book).order_by('hadith_number').first()
            if first_hadith:
                user.current_hadith_number = first_hadith.hadith_number
        else:
            first_book = Book.objects.annotate(cnt=Count('hadiths')).filter(cnt__gt=0).order_by('order').first()
            user.current_hadith_book = first_book
            first_hadith = Hadith.objects.filter(book=first_book).order_by('hadith_number').first()
            if first_hadith:
                user.current_hadith_number = first_hadith.hadith_number
