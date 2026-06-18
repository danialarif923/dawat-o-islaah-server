from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField


class SyncStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    last_page = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=150, unique=True)
    order = models.PositiveIntegerField(default=0)  # 👈 custom book order

    class Meta:
        ordering = ['order']  # custom ordering in admin & queries

    def __str__(self):
        return self.name

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chapters")
    chapter_number = models.IntegerField()
    chapter_english = models.CharField(max_length=255)
    chapter_arabic = models.CharField(max_length=255, blank=True, null=True)
    chapter_urdu = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('book', 'chapter_number')
        ordering = ['chapter_number']

    def __str__(self):
        return f"{self.chapter_number}. {self.chapter_english}"


class Baab(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="baabs")
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True, related_name="baabs"
    )
    chapter_english = models.CharField(max_length=255)
    baab_name_urdu = models.CharField(max_length=255)
    baab_name_english = models.CharField(max_length=255, blank=True, null=True)
    start_hadith_number = models.IntegerField()
    end_hadith_number = models.IntegerField()

    def __str__(self):
        return f"{self.book.name} - {self.baab_name_urdu} ({self.start_hadith_number}-{self.end_hadith_number})"

class Hadith(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="hadiths"
    )

    chapter_english = models.CharField(max_length=255)
    chapter_arabic = models.CharField(max_length=255, blank=True, null=True)
    chapter_urdu = models.CharField(max_length=255, blank=True, null=True)
    chapter_number = models.IntegerField(default=0)  # 👈 NEW FIELD
    hadith_number = models.IntegerField()
    baab = models.ForeignKey(Baab, on_delete=models.SET_NULL, null=True, blank=True, related_name="hadiths")
    arabic_text = RichTextField(config_name="default", blank=True, null=True)
    english_text = RichTextField(config_name="default", blank=True, null=True)
    urdu_text = RichTextField(config_name="default", blank=True, null=True)
    reference = RichTextField(config_name="default", blank=True, null=True)
    chapter_hadith_id = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, blank=True, null=True,
        choices=[
            ("Sahih", "Sahih"),
            ("Hasan", "Hasan"),
            ("Daif", "Da'if"),
            ("Maudu", "Maudu'"),
            ("Marfu", "Marfu'"),
            ("Mawquf", "Mawquf"),
            ("Maqtu", "Maqtu'"),
            ("Mutawatir", "Mutawatir"),
            ("Ahad", "Ahad"),
        ]
    )
    detailed_explanation = RichTextField(config_name="default", blank=True, null=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["book", "hadith_number"],
                name="unique_hadith_per_book"
            )
        ]
        ordering = ['book__order', 'chapter_number', 'hadith_number']

    def __str__(self):
        return f"{self.book.name} | Ch.{self.chapter_number} | {self.hadith_number}"


class HadithDocumentUpload(models.Model):
    file = models.FileField(
        upload_to='hadith_uploads/',
        verbose_name="Word Document (.docx)"
    )
    result_log = models.TextField(blank=True, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Upload Word Document"
        verbose_name_plural = "Upload Word Document"

    def __str__(self):
        if self.uploaded_at:
            return f"Upload {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
        return "Upload (pending)"
