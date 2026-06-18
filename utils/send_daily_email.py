import requests
import pytz
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.daily_content.daily_content_service import get_daily_content

User = get_user_model()

def get_fajr_time(lat, lon):
    """Fetch real-time Fajr timings based on user coordinates."""
    try:
        # Method 2 is the ISNA method
        url = f"http://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['timings']['Fajr']
    except Exception as e:
        print(f"API Error: {e}")
    return "05:00"  # Fallback

def send_daily_ayat_hadith():
    verse, hadith = get_daily_content()
    # Ensure we use the correct date context for the server
    today_date = timezone.now().date()

    # Filter for active users who want emails and haven't received one yet today
    users = User.objects.filter(
        is_active=True, 
        receive_daily_email=True
    ).exclude(last_email_sent_date=today_date)

    for user in users:
        # Defaults for Islamabad if coordinates aren't set
        lat = user.latitude or 33.6844
        lon = user.longitude or 73.0479
        user_tz_str = user.timezone or 'Asia/Karachi'
        
        try:
            user_tz = pytz.timezone(user_tz_str)
            user_local_time = datetime.now(user_tz)
            
            fajr_str = get_fajr_time(lat, lon) # e.g., "04:48"
            
            # Create a full datetime object for today's Fajr in the user's specific timezone
            fajr_time_today = user_tz.localize(datetime.combine(
                today_date, 
                datetime.strptime(fajr_str, "%H:%M").time()
            ))

            # LOGIC: Send if the current local time is at or after Fajr time
            if user_local_time >= fajr_time_today:
                print(f"Sending Fajr reminder to {user.email} (Local time: {user_local_time.strftime('%H:%M')}, Fajr was: {fajr_str})")
                
                message = f"""
Assalamualaikum {user.first_name},

Here is your Daily Islamic Reminder.

📖 Quran Verse:
{verse['arabic']}
{verse['urdu']}
{verse['english']}
Reference: {verse['reference']}

🕌 Hadith of the Day:
{hadith['arabic']}
{hadith['urdu']}
{hadith['english']}
Reference: {hadith['reference']}

May Allah bless your day.
"""
                send_mail(
                    "Daily Ayat & Hadith",
                    message,
                    None,
                    [user.email],
                    fail_silently=False
                )

                # Update field to prevent re-sending during the next hourly cron run
                user.last_email_sent_date = today_date
                user.save(update_fields=['last_email_sent_date'])
            else:
                print(f"Skipping {user.email}: It is not Fajr yet in {user_tz_str}")

        except Exception as e:
            print(f"Error processing {user.email}: {e}")
