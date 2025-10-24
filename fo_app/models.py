from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from datetime import timedelta
from .utils.mail import kirim_email_pengingat_stok

# 1. Interface User - Base Class
class AbstrakPengguna(models.Model):
    _id_keluarga = models.IntegerField()
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=False)
    _password = models.CharField(max_length=255)
    tanggal_lahir = models.DateField()
    jenis_kelamin = models.BooleanField()
    is_admin = models.BooleanField(default=False)
    poin = models.IntegerField(db_column='poin', default=0)
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self._id_keluarga} | {self.nama} | {self.email}'

    # Getter
    def get_id_keluarga(self):
        return self._id_keluarga
    
    def get_password(self):
        return self._password
    
    # Setter
    def set_id_keluarga(self, id_keluarga):
        self._id_keluarga = id_keluarga
    
    def set_password(self, password):
        self._password = password
    
    # Metode
    def tambah_poin(self, jumlah):
        if jumlah > 0:
            self.poin += jumlah
            self.save()

    def get_role(self):
        return "User"

    def can_create_task(self):
        return False
    
    # Metode abstrak untuk mengecek apakah pengguna memiliki akses suatu fitur
    def bisa_akses_fitur(self):
        raise NotImplementedError('Subkelas harus mengimplementasi metode bisa_akses_fitur()')
    
    # Polymorphism pengingat stok habis
    def ingatkan_stok(self):
        print("Gagal mengirimkan notifikasi karena pengguna ini bukan Admin")
    
# 2. Admin Inheritance
class Admin(AbstrakPengguna):
    def get_role(self):
        return "Admin"

    def can_create_task(self):
        return True
    
    # Implementasi metode abstrak
    def bisa_akses_fitur(self, nama_fitur: str):
        nama_fitur = nama_fitur.lower()
        # True artinya punya izin akses fitur tersebut
        akses = {
            'manajemen_pengguna': True,
            'manajemen_tugas': True,
            'manajemen_keuangan': True,
            'manajemen_barang': True,
            'lihat_statistik': True
        }

        # Jika nama fitur tidak ditemukan maka kembalikan False
        if nama_fitur not in akses:
            print(f'Nama fitur {nama_fitur} tidak ditemukan')
            return False
        
        # Kembalikan nilai boolean
        return akses[nama_fitur]
    
    # Polymorphism pengingat stok habis
    def ingatkan_stok(self):
        sekarang = timezone.now()

        # Ambil semua stok milik keluarga ini
        stok_list = Stok.objects.filter(_id_keluarga=self._id_keluarga)

        for stok in stok_list:
            # Hitung kapan terakhir kali notifikasi boleh dikirim berdasarkan interval_habis
            if stok.terakhir_diingatkan:
                waktu_berikutnya = stok.terakhir_diingatkan + timedelta(days=stok.interval_habis)
            else:
                # Jika belum pernah diingatkan, pakai tanggal_dibuat
                waktu_berikutnya = stok.tanggal_dibuat + timedelta(days=stok.interval_habis)

            # Jika waktu saat ini sudah lewat dari waktu berikutnya, kirim notifikasi
            if sekarang >= waktu_berikutnya:
                print(f"🔔 Notifikasi stok habis: Stok '{stok.nama}' perlu dicek.")
                kirim_email_pengingat_stok(self, stok)

                # Update field terakhir_diingatkan
                stok.terakhir_diingatkan = sekarang
                stok.save(update_fields=['terakhir_diingatkan'])

# 3. Member Inheritance
class Member(AbstrakPengguna):
    def get_role(self):
        return "Member"

    def can_create_task(self):
        return False
    
    # Implementasi metode abstrak
    def bisa_akses_fitur(self, nama_fitur: str):
        nama_fitur = nama_fitur.lower()
        # True artinya punya izin akses fitur tersebut
        akses = {
            'manajemen_pengguna': False,
            'manajemen_tugas': False,
            'manajemen_keuangan': True,
            'manajemen_barang': True,
            'lihat_statistik': True
        }

        # Jika nama fitur tidak ditemukan maka kembalikan False
        if nama_fitur not in akses:
            print(f'Nama fitur {nama_fitur} tidak ditemukan')
            return False
        
        # Kembalikan nilai boolean
        return akses[nama_fitur]
    
    # Polymorphism pengingat stok habis
    def ingatkan_stok(self):
        print("Gagal mengirimkan notifikasi karena pengguna ini bukan Admin")

# 4. Tasks
class Tugas(models.Model):
    STATUS_CHOICES = [
        ('belum_selesai', 'Belum Selesai'),
        ('selesai', 'Selesai'),
    ]
    
    _id_keluarga = models.IntegerField()
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='belum_selesai'
    )
    poin = models.IntegerField(default=0)
    tenggat_waktu = models.DateTimeField()
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} | {self.judul}'

    # Getter
    def get_id_keluarga(self):
        return self._id_keluarga
    
    # Setter
    def set_id_keluarga(self, id_keluarga):
        self._id_keluarga = id_keluarga

    # Methods
    def is_telat(self):
        return timezone.now() > self.tenggat_waktu

# 5. Task Assignments
class Penugasan(models.Model):
    PERAN_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    pengguna = models.ForeignKey(AbstrakPengguna, on_delete=models.CASCADE)
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE)
    peran = models.CharField(max_length=50, choices=PERAN_CHOICES)

# 6. Stocks
class Stok(models.Model):
    _id_keluarga = models.IntegerField()
    nama = models.CharField(max_length=255)
    jumlah = models.FloatField()
    satuan = models.CharField(max_length=50)
    interval_habis = models.IntegerField()
    terakhir_diingatkan = models.DateTimeField(null=True, blank=True)
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    # Getter
    def get_id_keluarga(self):
        return self._id_keluarga
    
    # Setter
    def set_id_keluarga(self, id_keluarga):
        self._id_keluarga = id_keluarga

# 7. Transaksi Keuangan
class TransaksiKeuangan(models.Model):
    JENIS_CHOICES = [
        ('pemasukan', 'Pemasukan'),
        ('pengeluaran', 'Pengeluaran')
    ]
    _id_keluarga = models.IntegerField()
    pengguna = models.ForeignKey('AbstrakPengguna', on_delete=models.CASCADE, related_name='transaksi_keuangan')
    nama = models.CharField(max_length=255)
    nominal = models.FloatField()
    tanggal_transaksi = models.DateTimeField()
    jenis = models.CharField(max_length=50, choices=JENIS_CHOICES, help_text="pemasukan atau pengeluaran")
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    # Getter
    def get_id_keluarga(self):
        return self._id_keluarga
    
    # Setter
    def set_id_keluarga(self, id_keluarga):
        self._id_keluarga = id_keluarga

# 8. Token Login
class TokenLogin(models.Model):
    _id_keluarga = models.IntegerField()
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    _token = models.CharField(max_length=255)
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    # Getter
    def get_id_keluarga(self):
        return self._id_keluarga
    
    def get_token(self):
        return self._token
    
    # Setter
    def set_id_keluarga(self, id_keluarga):
        self._id_keluarga = id_keluarga
    
    def set_token(self, token):
        self._token = token