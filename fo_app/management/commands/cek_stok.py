from django.core.management.base import BaseCommand
from fo_app.models import Admin

class Command(BaseCommand):
    help = 'Kirim notifikasi stok habis berdasarkan interval'

    def handle(self, *args, **kwargs):
        for admin in Admin.objects.all():
            admin.ingatkan_stok()
        self.stdout.write(self.style.SUCCESS("Notifikasi stok habis berhasil dikirim"))
