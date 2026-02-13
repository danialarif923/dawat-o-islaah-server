from django.shortcuts import render
import json, os
from django.conf import settings
from .models import Ayat
from django.http import JsonResponse
from django.http import HttpResponse
from utils.fonts import generate_fonts_css
from .models import CustomFont
from django.views.decorators.cache import never_cache
from .models import Tafseer

def get_tafseer(request):

    surah = request.GET.get("surah")
    ayah = request.GET.get("ayah")

    if not surah or not ayah:
        return JsonResponse({
            "error": "surah and ayah required"
        }, status=400)

    try:
        tafseer = Tafseer.objects.get(
            surah=surah,
            ayat_number=ayah
        )

        return JsonResponse({
            "surah": surah,
            "ayah": ayah,
            "tafseer": tafseer.text
        })

    except Tafseer.DoesNotExist:

        return JsonResponse({
            "error": "Tafseer not found"
        }, status=404)
    
def get_custom_fonts(request):
    """
    API endpoint to get all custom fonts.
    Returns JSON array with font name and URL.
    Used by JavaScript to dynamically populate CKEditor font dropdown.
    """
    fonts = CustomFont.objects.all()

    data = []

    for f in fonts:
        data.append({
            "name": f.name,
            "url": f.file.url
        })

    return JsonResponse(data, safe=False)

@never_cache
def custom_fonts_css(request):
    fonts = CustomFont.objects.all()

    css = ""

    for font in fonts:
        css += f"""
        @font-face {{
            font-family: '{font.name}';
            src: url('{font.file.url}');
            font-weight: normal;
            font-style: normal;
        }}
        """

    response = HttpResponse(css, content_type="text/css")

    # 🚨 Disable cache
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response

def get_surah_ayat(request):

    data = load_quran_json()

    result = {}

    for item in data:
        surah = item["surah"]
        ayat = item["ayat"]

        if surah not in result:
            result[surah] = []

        result[surah].append(ayat)

    return JsonResponse(result)

def get_ayat(request):

    surah = request.GET.get("surah")
    ayat = request.GET.get("ayat")

    try:
        ayat_obj = Ayat.objects.get(
            surah=surah,
            ayat_number=ayat
        )

        return JsonResponse({
            "text": ayat_obj.text
        })

    except Ayat.DoesNotExist:

        return JsonResponse({
            "text": ""
        })
    
def load_quran_json():
    path = os.path.join(settings.BASE_DIR, 'quran/data/dailyVerse.json')

    with open(path, encoding="utf-8") as f:
        return json.load(f)
