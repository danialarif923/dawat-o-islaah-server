from django.db import models
from django.conf import settings
import re

from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField


# ===============================
# Custom Font Model
# ===============================

class CustomFont(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Font name shown in editor (e.g. Al Mushaf)"
    )

    file = models.FileField(
        upload_to="custom_fonts/",
        help_text="Upload .ttf or .otf font file"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(
        default=True,
        help_text="Enable / Disable this font"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ===============================
# Ayat Model
# ===============================

class Ayat(models.Model):

    surah = models.IntegerField()

    ayat_number = models.IntegerField()

    text = RichTextField(config_name="default")

    tafsir = RichTextField(
        blank=True,
        null=True,
        config_name="default"
    )

    audio = models.FileField(
        upload_to="ayat_audio/",
        null=True,
        blank=True
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_ayats"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("surah", "ayat_number")
        ordering = ["surah", "ayat_number"]

    def __str__(self):
        return f"Surah {self.surah} | Ayat {self.ayat_number}"


# ===============================
# Translation Model
# ===============================

class Translation(models.Model):

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("ur", "Urdu"),
    )

    author = models.CharField(max_length=150)

    surah = models.IntegerField()

    ayat_number = models.IntegerField()

    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES
    )

    text = models.TextField()

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_translations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "surah",
            "ayat_number",
            "language",
            "author"
        )

        ordering = ["surah", "ayat_number"]

    def __str__(self):
        return (
            f"{self.author} | "
            f"{self.get_language_display()} | "
            f"Ayat {self.ayat_number}"
        )

    def clean(self):

        urdu_regex = re.compile(r'[\u0600-\u06FF]')

        has_urdu = bool(urdu_regex.search(self.text))

        if has_urdu and self.language == "en":
            raise ValidationError(
                "You selected English but the text is in Urdu."
            )

        if not has_urdu and self.language == "ur":
            raise ValidationError(
                "You selected Urdu but the text is in English."
            )


# ===============================
# Tafseer Model
# ===============================

class Tafseer(models.Model):

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("ur", "Urdu"),
    )

    author = models.CharField(max_length=150)

    surah = models.IntegerField()

    ayat_number = models.IntegerField()

    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    text = models.TextField()

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_tafseers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "surah",
            "ayat_number",
            "author",
            "language"
        )

    ordering = ["surah", "ayat_number"]   # ASCENDING



    def __str__(self):
        return (
            f"{self.author} | "
            f"{self.get_language_display()} | "
            f"Ayat {self.ayat_number}"
        )

    def clean(self):

        urdu_regex = re.compile(r'[\u0600-\u06FF]')

        has_urdu = bool(urdu_regex.search(self.text))

        if has_urdu and self.language == "en":
            raise ValidationError(
                "You selected English but the text is in Urdu."
            )

        if not has_urdu and self.language == "ur":
            raise ValidationError(
                "You selected Urdu but the text is in English."
            )
