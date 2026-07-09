import sys
sys.path.insert(0, '/home/ubuntu/apps/dawat-o-islaah-server')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dawat_o_islaah.settings'

import django
django.setup()

from quran.models import CustomFont

print("Before switch:")
for f in CustomFont.objects.all():
    print(f"  id={f.id}, name={f.name}, file={f.file}, active={f.is_active}")

font = CustomFont.objects.create(
    name='kfgq-uthman-taha',
    file='custom_fonts/KFGQPC_Uthman_Taha_Naskh_Regular.ttf',
    is_active=True
)

print("\nAfter switch:")
for f in CustomFont.objects.all():
    print(f"  id={f.id}, name={f.name}, file={f.file}, active={f.is_active}")

print(f"\nNew font created: id={font.id}, name={font.name}")
