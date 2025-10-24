from django.contrib import admin
from .models import AbstrakPengguna, Admin, Member, Tugas, Penugasan, Stok, TransaksiKeuangan, TokenLogin

# Register your models here.
# 2. Admin model
class AdminAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "email", "tanggal_lahir", "jenis_kelamin", "is_admin", "tanggal_dibuat")
admin.site.register(Admin, AdminAdmin)

# 3. Member model
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "email", "tanggal_lahir", "jenis_kelamin", "is_admin", "tanggal_dibuat")
admin.site.register(Member, MemberAdmin)

# 4. Tugas model
class TugasAdmin(admin.ModelAdmin):
    list_display = ("id", "judul", "status", "tenggat_waktu", "tanggal_dibuat")
admin.site.register(Tugas, TugasAdmin)

# 5. Penugasan model
class PenugasanAdmin(admin.ModelAdmin):
    list_display = ("id", "pengguna", "tugas", "peran")
admin.site.register(Penugasan, PenugasanAdmin)

# 6. Stok model
class StokAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "jumlah", "satuan", "interval_habis", "terakhir_diingatkan", "tanggal_dibuat", "tanggal_diubah")
admin.site.register(Stok, StokAdmin)

# 7. Transaksi Keuangan model
class TransaksiKeuanganAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "pengguna", "nominal", "jenis", "tanggal_transaksi", "tanggal_dibuat")
admin.site.register(TransaksiKeuangan, TransaksiKeuanganAdmin)

# 8. TokenLogin model
class TokenLoginAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_admin", "_token", "tanggal_dibuat")
admin.site.register(TokenLogin, TokenLoginAdmin)