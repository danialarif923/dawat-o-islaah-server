from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.http import HttpResponseRedirect

from .models import Ayat, Translation, Tafseer, CustomFont
from .widgets import DynamicCKEditorWidget


# =====================================================
# Ayat Admin Form (Dynamic CKEditor with Custom Fonts)
# =====================================================

class AyatAdminForm(forms.ModelForm):

    class Meta:
        model = Ayat
        fields = "__all__"

        widgets = {
            "text": DynamicCKEditorWidget(),
            "tafsir": DynamicCKEditorWidget(),
        }



# =====================================================
# Ayat Admin
# =====================================================

@admin.register(Ayat)
class AyatAdmin(admin.ModelAdmin):

    form = AyatAdminForm

    list_display = ("surah", "ayat_number", "audio_player", "created_at")

    list_filter = ("surah",)

    search_fields = ("text",)

    readonly_fields = ("audio_player",)

    fields = (
        "surah",
        "ayat_number",
        "text",
        "audio",
        "audio_player",
    )

    ordering = ("surah", "ayat_number")


    def audio_player(self, obj):

        if obj.audio:
            return format_html(
                """
                <audio controls style="width:200px;">
                    <source src="{}" type="audio/mpeg">
                    Your browser does not support audio.
                </audio>
                """,
                obj.audio.url
            )

        return "No Audio"


    audio_player.short_description = "Audio Preview"


    def save_model(self, request, obj, form, change):

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


    class Media:

        js = (
            "js/quran_data.js",
            "js/ayat_admin.js",
            "quran/js/ckeditor_custom.js",  # Add custom font loader
        )

        css = {
            "all": (
                "quran/fonts.css",
            )
        }



# =====================================================
# Custom Font Admin
# =====================================================

@admin.register(CustomFont)
class CustomFontAdmin(admin.ModelAdmin):

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(request.path)

    def response_change(self, request, obj):
        return HttpResponseRedirect(request.path)

    list_display = ("name", "font_preview", "file", "uploaded_at")

    search_fields = ("name",)
    
    def font_preview(self, obj):
        """Show a preview of the font in the admin list"""
        return format_html(
            '<span style="font-family: \'{}\'; font-size: 18px;">Sample Text • نمونہ متن • عربي</span>',
            obj.name
        )
    
    font_preview.short_description = "Preview"



# =====================================================
# Translation Admin
# =====================================================

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):

    list_display = (
        "author",
        "language",
        "surah",
        "ayat_number",
        "created_at",
    )

    list_filter = ("language", "surah", "author")

    search_fields = ("text", "author")


    def save_model(self, request, obj, form, change):

        obj.updated_by = request.user
        obj.full_clean()
        super().save_model(request, obj, form, change)


    class Media:

        js = (
            "js/quran_data.js",
            "js/ayat_admin.js",
        )

        css = {
            "all": (
                "quran/fonts.css",
            )
        }


# =====================================================
# Tafseer Admin
# =====================================================

@admin.register(Tafseer)
class TafseerAdmin(admin.ModelAdmin):

    list_display = (
        "author",
        "language",
        "surah",
        "ayat_number",
        "created_at",
    )
    ordering = ("surah", "ayat_number")

    list_filter = ("language", "surah", "author")

    search_fields = ("text", "author")


    def save_model(self, request, obj, form, change):

        obj.updated_by = request.user
        obj.full_clean()
        super().save_model(request, obj, form, change)


    class Media:

        js = (
            "js/quran_data.js",
            "js/tafseer_admin.js",
        )

        css = {
            "all": (
                "quran/fonts.css",
            )
        }
