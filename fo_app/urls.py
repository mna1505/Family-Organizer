from django.urls import path
from .views import beranda, signup, login_baru, login, daftar_tugas, input_keuangan, statistik, daftar_barang, post_signup, post_tambah_pengguna, daftar_pengguna, post_login, post_login_baru, logout, delete_pengguna, delete_diri, ubah_peran_pengguna, detail_pengguna, detail_tugas, post_tambah_tugas, put_status_tugas, delete_tugas, detail_barang, delete_barang, post_tambah_barang, input_pemasukan, input_pengeluaran, post_tambah_pemasukan, post_tambah_pengeluaran, get_statistik_keuangan, get_statistik_poin_kontribusi, histori_keuangan, generate_data_dummy

urlpatterns = [
    path('', beranda, name='beranda'),
    path('generate_data_dummy/', generate_data_dummy, name='generate_data_dummy'),
    path('signup/', signup, name='signup'),
    path('post_signup/', post_signup, name='post_signup'),
    path('login_baru/', login_baru, name='login_baru'),
    path('login/', login, name='login'),
    path('post_login/', post_login, name='post_login'),
    path('post_login_baru/', post_login_baru, name='post_login_baru'),
    path('logout/', logout, name='logout'),
    path('daftar_pengguna/', daftar_pengguna, name='daftar_pengguna'),
    path('detail_pengguna/<int:id>/', detail_pengguna, name='detail_pengguna'),
    path('delete_pengguna/<int:id>/', delete_pengguna, name='delete_pengguna'),
    path('delete_diri/', delete_diri, name='delete_diri'),
    path('post_tambah_pengguna/', post_tambah_pengguna, name='post_tambah_pengguna'),
    path('ubah_peran_pengguna/<int:id>/<str:peran_baru>/', ubah_peran_pengguna, name='ubah_peran_pengguna'),
    path('daftar_tugas/', daftar_tugas, name='daftar_tugas'),
    path('post_tambah_tugas/', post_tambah_tugas, name='post_tambah_tugas'),
    path('detail_tugas/<int:id>/', detail_tugas, name='detail_tugas'),
    path('put_status_tugas/<int:id>/', put_status_tugas, name='put_status_tugas'),
    path('delete_tugas/<int:id>/', delete_tugas, name='delete_tugas'),
    path('input_keuangan/', input_keuangan, name='input_keuangan'),
    path('statistik/', statistik, name='statistik'),
    path('daftar_barang/', daftar_barang, name='daftar_barang'),
    path('detail_barang/<int:id>/', detail_barang, name='detail_barang'),
    path('delete_barang/<int:id>/', delete_barang, name='delete_barang'),
    path('post_tambah_barang/', post_tambah_barang, name='post_tambah_barang'),
    path('input_pemasukan/', input_pemasukan, name='input_pemasukan'),
    path('input_pengeluaran/', input_pengeluaran, name='input_pengeluaran'),
    path('post_tambah_pemasukan/', post_tambah_pemasukan, name='post_tambah_pemasukan'),
    path('post_tambah_pengeluaran/', post_tambah_pengeluaran, name='post_tambah_pengeluaran'),
    path('get_statistik_keuangan/', get_statistik_keuangan, name='get_statistik_keuangan'),
    path('get_statistik_poin_kontribusi/', get_statistik_poin_kontribusi, name='get_statistik_poin_kontribusi'),
    path('histori_keuangan/', histori_keuangan, name='histori_keuangan')
]

"""
Halaman:
Admin:
- beranda
- signup
- login (baru (lewat email))
- login (lama)
- tambah tugas (create : judul, deskripsi, deadline, poin, ditugaskan kepada siapa)
- daftar tugas (menu: edit, hapus, selesaikan tugas)
- input pemasukan atau pengeluaran finansial
- statistik (poin tugas dan finansial)
- daftar barang
- tambah barang (create : nama, jumlah, satuan, interval habis)

Member:
- beranda
- login (baru (lewat email))
- login (lama)
- daftar tugas (menu: selesaikan tugas)
- input pemasukan atau pengeluaran finansial
- statistik (poin tugas, dan finansial)
- daftar barang
- tambah barang (create : nama, jumlah, satuan, interval habis)
 """