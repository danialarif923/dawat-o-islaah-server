from django.db import models
from django.utils.translation import gettext_lazy as _

class Book(models.Model):
    title = models.CharField(_('title'), max_length=200)
    author = models.CharField(_('author'), max_length=100, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    pdf_file = models.FileField(_('PDF file'), upload_to='books/pdfs/')
    cover_image = models.ImageField(_('cover image'), upload_to='books/covers/', blank=True, null=True)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_public = models.BooleanField(_('is public'), default=True)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ('-uploaded_at',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('book_detail', args=[str(self.id)])