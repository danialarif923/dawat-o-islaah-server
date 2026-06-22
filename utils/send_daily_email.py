import requests
import pytz
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.daily_content.daily_content_service import get_daily_content, advance_daily_content

User = get_user_model()


def get_fajr_time(lat, lon):
    try:
        url = 'http://api.aladhan.com/v1/timings?latitude={}&longitude={}&method=2'.format(lat, lon)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['timings']['Fajr']
    except Exception as e:
        print('API Error: {}'.format(e))
    return '05:00'


def send_daily_ayat_hadith():
    today_date = timezone.now().date()

    users = User.objects.filter(
        is_active=True,
        receive_daily_email=True
    ).exclude(last_email_sent_date=today_date)

    for user in users:
        lat = user.latitude or 33.6844
        lon = user.longitude or 73.0479
        user_tz_str = user.timezone or 'Asia/Karachi'

        try:
            user_tz = pytz.timezone(user_tz_str)
            user_local_time = datetime.now(user_tz)

            fajr_str = get_fajr_time(lat, lon)

            fajr_time_today = user_tz.localize(datetime.combine(
                today_date,
                datetime.strptime(fajr_str, '%H:%M').time()
            ))

            if user_local_time >= fajr_time_today:
                verse, hadith = get_daily_content(user)

                print('Sending Fajr reminder to {} (Local time: {}, Fajr was: {})'.format(
                    user.email, user_local_time.strftime('%H:%M'), fajr_str))
                print('  Verse: {} | Hadith: {}'.format(verse['reference'], hadith['reference']))

                message = '''
Assalamualaikum {},

Here is your Daily Islamic Reminder.

📖 Quran Verse:
{}
{}
{}
Reference: {}

🕌 Hadith of the Day:
{}
{}
{}
Reference: {}

May Allah bless your day.
'''.format(
    user.first_name,
    verse['arabic'], verse['urdu'], verse['english'], verse['reference'],
    hadith['arabic'], hadith['urdu'], hadith['english'], hadith['reference'],
)

                send_mail(
                    'Daily Ayat & Hadith',
                    message,
                    None,
                    [user.email],
                    fail_silently=False
                )

                advance_daily_content(user)
                user.last_email_sent_date = today_date
                user.save(update_fields=[
                    'last_email_sent_date',
                    'current_verse_surah',
                    'current_verse_ayah',
                    'current_hadith_book',
                    'current_hadith_number',
                ])
            else:
                print('Skipping {}: It is not Fajr yet in {}'.format(user.email, user_tz_str))

        except Exception as e:
            print('Error processing {}: {}'.format(user.email, e))