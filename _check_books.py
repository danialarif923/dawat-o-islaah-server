from hadith.models import Book
for b in Book.objects.all().order_by("order"):
    print(b.id, repr(b.name), b.order, b.hadiths.count())
