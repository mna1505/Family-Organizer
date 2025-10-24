import re
from itertools import chain
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.utils import timezone
from datetime import datetime
from collections import defaultdict
from .models import Admin, Member, Tugas, Penugasan, Stok, TransaksiKeuangan, TokenLogin
from django.contrib import messages
from .utils.post_signup import generate_id_keluarga_unik, is_email_tersedia
from .utils.post_login_baru import generate_token_login_unik
from .utils.pengguna import set_sesi_pengguna
from .utils.mail import kirim_mail_undangan
from .utils.post_tambah_pengguna import get_link_login
from .utils.tanggal import format_tanggal_indonesia
from .utils.populate_dummy import generate_dummy_family_data
from django.http import JsonResponse, HttpResponseForbidden

# Halaman untuk generate data dummy
def generate_data_dummy(request):
    generate_dummy_family_data(123456, 3)
    generate_dummy_family_data(123457, 2)
    generate_dummy_family_data(123458, 5)
    return HttpResponse('Data dummy berhasil dibuat')

# Halaman beranda
def beranda(request):
    context = {}
    return render(request, 'beranda.html', context)

# Halaman form pendaftaran admin
def signup(request):
    context = {}
    return render(request, 'signup.html', context)

def post_signup(request):
    if request.method == 'POST':
        # Ambil data dari formulir
        nama = request.POST.get('nama', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        konfirmasi_password = request.POST.get('konfirmasi_password', '')
        tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
        jenis_kelamin_str = request.POST.get('jenis_kelamin', '0').strip()

        # Inisialisasi data tambahan
        is_admin = True
        poin = 0
        id_keluarga = generate_id_keluarga_unik()

        # --- Mulai validasi input ---
        # Validasi nama
        if not nama:
            messages.error(request, "Nama tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Validasi email
        if not email:
            messages.error(request, "Email tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Format email tidak valid.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not is_email_tersedia(email):
            messages.error(request, f"Email '{email}' sudah terdaftar.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Validasi password
        if len(password) < 6:
            messages.error(request, "Password minimal 6 karakter.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif password != konfirmasi_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Validasi tanggal lahir
        try:
            datetime.strptime(tanggal_lahir, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Format tanggal lahir tidak valid (gunakan YYYY-MM-DD).")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        tanggal_lahir_naive = datetime.fromisoformat(tanggal_lahir)
        tanggal_lahir = timezone.make_aware(tanggal_lahir_naive)

        try:
            if tanggal_lahir > timezone.now():
                messages.error(request, "Tanggal lahir tidak boleh di masa depan")
                return redirect(request.META.get('HTTP_REFERER', '/'))
        except ValueError:
                messages.error(request, "Format tanggal lahir tidak valid")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # Validasi jenis kelamin
        if jenis_kelamin_str not in ['0', '1']:
            messages.error(request, "Jenis kelamin tidak valid.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        jenis_kelamin = int(jenis_kelamin_str) == 1  # 1 = Laki-laki, 0 = Perempuan

        # --- Akhir validasi input ---

        admin = Admin(nama=nama, email=email, tanggal_lahir=tanggal_lahir, jenis_kelamin=jenis_kelamin, is_admin=is_admin, poin=poin)
        admin.set_id_keluarga(id_keluarga)
        admin.set_password(password)

        admin.save()

        tanggal_lahir_str = str(tanggal_lahir)
        jenis_kelamin_num_str = '1' if jenis_kelamin else '0'
        is_admin_num_str = '1' if is_admin else '0'
        poin_str = str(poin)

        set_sesi_pengguna(request, id_keluarga, nama, email, password, tanggal_lahir_str, jenis_kelamin_num_str, is_admin_num_str, poin_str)

        return redirect('daftar_pengguna')
    else:
        return HttpResponseForbidden('Tidak diizinkan.')

# Halaman login via email (link token)
def login_baru(request):
    # Ambil token dari url
    token = request.GET.get('token', '')

    # Jika token kosong maka error
    if not token.strip():
        return HttpResponseForbidden('Anda tidak memiliki akses pada halaman ini')

    list_token = TokenLogin.objects.filter(_token=token)

    # Jika token tidak ditemukan maka error
    is_token_ada = list_token.exists()
    if not is_token_ada:
        return HttpResponseForbidden('Token Anda tidak valid, tidak dapat mengakses halaman ini')

    # Ambil data token pertama
    token = list_token[0]

    # Ubah ke format string
    id_keluarga_str = str(token.get_id_keluarga())
    email = token.email
    is_admin_num_str = '1' if token.is_admin else '0'

    # Render halaman login baru
    context = {
        'id_keluarga_str': id_keluarga_str,
        'email': email,
        'is_admin_num_str': is_admin_num_str
    }
    return render(request, 'login_baru.html', context)

def post_login_baru(request):
    if request.method == "POST":
        # Ambil data dari formulir
        nama = request.POST.get('nama', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        konfirmasi_password = request.POST.get('konfirmasi_password', '')
        tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
        jenis_kelamin = request.POST.get('jenis_kelamin', '').strip()
        id_keluarga = request.POST.get('id_keluarga', '').strip()
        is_admin = request.POST.get('is_admin', '').strip()
        poin = 0

        # --- Validasi nama ---
        if not nama:
            messages.error(request, "Nama tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi email ---
        if not email:
            messages.error(request, "Email tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Format email tidak valid.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi password ---
        if not password:
            messages.error(request, "Password tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif len(password) < 6:
            messages.error(request, "Password minimal 6 karakter.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif password != konfirmasi_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi tanggal lahir ---
        try:
            datetime.strptime(tanggal_lahir, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Format tanggal lahir tidak valid (gunakan YYYY-MM-DD).")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        tanggal_lahir_naive = datetime.fromisoformat(tanggal_lahir)
        tanggal_lahir = timezone.make_aware(tanggal_lahir_naive)

        try:
            if tanggal_lahir > timezone.now():
                messages.error(request, "Tanggal lahir tidak boleh di masa depan")
                return redirect(request.META.get('HTTP_REFERER', '/'))
        except ValueError:
                messages.error(request, "Format tanggal lahir tidak valid")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi jenis kelamin ---
        if jenis_kelamin not in ['0', '1']:
            messages.error(request, "Jenis kelamin tidak valid.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        jenis_kelamin = int(jenis_kelamin) == 1  # True jika laki-laki

        # --- Validasi id_keluarga dan is_admin ---
        try:
            id_keluarga_int = int(id_keluarga)
            is_admin_boolean = int(is_admin) == 1
        except ValueError:
            messages.error(request, "ID keluarga dan status admin harus berupa angka.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi token data tersembunyi ---
        list_token = TokenLogin.objects.filter(
            _id_keluarga=id_keluarga_int,
            email=email,
            is_admin=is_admin_boolean
        )
        if not list_token.exists():
            messages.error(request, "Terjadi kesalahan, mohon masukkan ulang data.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Lolos semua validasi ---

        # Hapus data pengguna baru dari tabel TokenLogin
        token = list_token[0]
        token.delete()

        # Simpan data
        jenis_kelamin_boolean = int(jenis_kelamin) == 1
        if is_admin_boolean:
            admin = Admin(nama=nama, email=email, tanggal_lahir=tanggal_lahir, jenis_kelamin=jenis_kelamin_boolean, is_admin=is_admin_boolean, poin=poin)
            admin.set_id_keluarga(id_keluarga_int)
            admin.set_password(password)
            admin.save()
        else:
            member = Member(nama=nama, email=email, tanggal_lahir=tanggal_lahir, jenis_kelamin=jenis_kelamin_boolean, is_admin=is_admin_boolean, poin=poin)
            member.set_id_keluarga(id_keluarga)
            member.set_password(password)
            member.save()
        
        # Membuat sesi
        poin_str = str(poin)
        tanggal_lahir_str = str(tanggal_lahir)
        set_sesi_pengguna(request, id_keluarga, nama, email, password, tanggal_lahir_str, jenis_kelamin, is_admin, poin_str)

        # Masuk ke halaman beranda
        return redirect('daftar_tugas')
    else:
        return HttpResponseForbidden('Tidak diizinkan.')

def logout(request):
    # Set sesi menjadi kosong agar website lupa dengan data pengguna
    set_sesi_pengguna(request, '', '', '', '', '', '', '', '')
    return redirect('beranda')

def delete_pengguna(request, id):
    if request.method == "GET":
        # Ambil data pengguna
        pengguna = request.pengguna
        email = pengguna.email
        id_keluarga = pengguna.get_id_keluarga()

        # Tolak akses jika tidak memiliki izin
        nama_fitur = 'manajemen_pengguna'
        bisa_akses = pengguna.bisa_akses_fitur(nama_fitur)
        if not bisa_akses:
            return JsonResponse({
                'status': 'error',
                'message': 'Anda tidak memiliki akses fitur ini.'
            }, status=403)

        # if not is_admin:
            # return JsonResponse({
            #     'status': 'error',
            #     'message': 'Anda tidak memiliki akses fitur ini karena Anda bukan admin'
            # }, status=403)

        # try:
        #     target_pengguna = AbstrakPengguna.objects.get(id=id, id_keluarga=pengguna.get_id_keluarga())
        # except AbstrakPengguna.DoesNotExist:
        #     return JsonResponse({
        #         'status': 'error',
        #         'message': 'Pengguna tidak ditemukan'
        #     }, status=404)

        # Mulai proses penghapusan
        # Ambil data pengguna
        target_admin = Admin.objects.filter(id=id, _id_keluarga=id_keluarga).first()
        target_member = Member.objects.filter(id=id, _id_keluarga=id_keluarga).first()
        target_pengguna = None

        # Mengecek apakah data ada
        if not target_admin is None:
            target_pengguna = target_admin
        elif not target_member is None:
            target_pengguna = target_member
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Pengguna tidak Ditemukan'
            }, status=404)
        
        # Mengecek apakah pengguna merupakan admin itu sendiri
        if target_pengguna.email.lower() == email.lower():
            return JsonResponse({
                'status': 'error',
                'message': 'Tidak dapat menghapus diri Anda sendiri'
            }, status=400)

        # Hapus jika ada
        target_pengguna.delete()
        
        # Akhir proses penghapusan
        return JsonResponse({
            'status': 'success',
            'message': 'Akun Telah Dihapus'
        })

    else:
        return HttpResponseForbidden('Tidak diizinkan')

def delete_diri(request):
    if request.method == "GET":
        # Ambil data pengguna dari sesi
        pengguna = request.pengguna
        email = pengguna.email
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil semua admin dan member dari keluarga tersebut
        daftar_admin = Admin.objects.filter(_id_keluarga=id_keluarga)
        daftar_member = Member.objects.filter(_id_keluarga=id_keluarga)
        list_pengguna = list(chain(daftar_admin, daftar_member))

        # Temukan target pengguna berdasarkan email
        target_pengguna = next((p for p in list_pengguna if p.email == email), None)

        # Jika tidak ditemukan
        if target_pengguna is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Akun Anda Tidak Ditemukan'
            }, status=404)

        # Jika bukan admin → hapus akun langsung
        if not is_admin:
            target_pengguna.delete()
            set_sesi_pengguna(request, '', '', '', '', '', '', '', '')
            return JsonResponse({
                'status': 'success',
                'message': 'Akun berhasil dihapus',
                'redirect_url': '/'
            })

        # Jika hanya ada 1 pengguna dalam keluarga → hapus langsung
        if len(list_pengguna) == 1:
            target_pengguna.delete()
            set_sesi_pengguna(request, '', '', '', '', '', '', '', '')
            return JsonResponse({
                'status': 'success',
                'message': 'Akun berhasil dihapus',
                'redirect_url': '/'
            })

        # Filter semua admin
        list_admin = [p for p in list_pengguna if p.is_admin]

        # Jika masih ada admin lain selain dirinya → hapus langsung
        if len(list_admin) > 1:
            target_pengguna.delete()
            set_sesi_pengguna(request, '', '', '', '', '', '', '', '')
            return JsonResponse({
                'status': 'success',
                'message': 'Akun berhasil dihapus',
                'redirect_url': '/'
            })

        # Jika hanya ada 1 admin (diri sendiri), dan masih ada member
        if len(list_admin) == 1 and len(list_pengguna) > 1:
            # Cari member tertua (diluar target_pengguna)
            kandidat_member = [p for p in list_pengguna if p.email != email and not p.is_admin]
            member_tertua = sorted(kandidat_member, key=lambda x: x.tanggal_lahir)[0] if kandidat_member else None

            if member_tertua is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Member tertua tidak ditemukan',
                    'redirect_url': '/'
                }, status=400)

            print("Member tertua:", member_tertua.email, member_tertua.nama)

            # Simpan datanya
            target_nama = member_tertua.nama
            target_email = member_tertua.email
            target_password = member_tertua.get_password()
            target_tanggal_lahir = member_tertua.tanggal_lahir
            target_jenis_kelamin = member_tertua.jenis_kelamin
            target_poin = member_tertua.poin

            # Hapus member tertua
            member_tertua.delete()

            # Buat akun admin baru dari data member
            admin_baru = Admin(
                nama=target_nama,
                email=target_email,
                tanggal_lahir=target_tanggal_lahir,
                jenis_kelamin=target_jenis_kelamin,
                is_admin=True,
                poin=target_poin
            )
            admin_baru.set_id_keluarga(id_keluarga)
            admin_baru.set_password(target_password)
            admin_baru.save()

            # Hapus akun sendiri dan logout
            target_pengguna.delete()
            set_sesi_pengguna(request, '', '', '', '', '', '', '', '')

            return JsonResponse({
                'status': 'success',
                'message': 'Akun berhasil dihapus. Member tertua telah dijadikan admin secara otomatis.',
                'redirect_url': '/'
            })

        # Jika tidak memenuhi semua kondisi
        return JsonResponse({
            'status': 'error',
            'message': 'Telah terjadi kesalahan saat menghapus akun.'
        }, status=400)
    else:
        return HttpResponseForbidden('Tidak diizinkan')

def login(request):
    context = {}
    return render(request, 'login.html', context)

def post_login(request):
    if request.method == 'POST':
        # Ambil data dari formulir
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # --- Validasi email ---
        if not email:
            messages.error(request, "Email tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Format email tidak valid.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # --- Validasi password ---
        if not password:
            messages.error(request, "Password tidak boleh kosong.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        # --- Lolos validasi ---

        # Ambil data pengguna berdasarkan email dari kedua model turunan
        pengguna = None
        if Admin.objects.filter(email=email).exists():
            pengguna = Admin.objects.get(email=email)
        elif Member.objects.filter(email=email).exists():
            pengguna = Member.objects.get(email=email)

        # Jika pengguna tidak ditemukan
        if pengguna is None:
            messages.error(request, f"Email '{email}' belum terdaftar")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Validasi password
        isPasswordValid = pengguna.get_password() == password
        if not isPasswordValid:
            messages.error(request, 'Password salah')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Mengubah data ke format string
        tanggal_lahir_str = str(pengguna.tanggal_lahir)
        jenis_kelamin_num_str = '1' if pengguna.jenis_kelamin else '0'
        is_admin_num_str = '1' if pengguna.is_admin else '0'
        poin_str = str(pengguna.poin)

        # Menyimpan data pengguna di sesi
        set_sesi_pengguna(
            request,
            pengguna.get_id_keluarga(),
            pengguna.nama,
            pengguna.email,
            pengguna.get_password(),
            tanggal_lahir_str,
            jenis_kelamin_num_str,
            is_admin_num_str,
            poin_str
        )

        return redirect('daftar_pengguna')
    else:
        return HttpResponseForbidden('Tidak diizinkan.')

def daftar_pengguna(request):
    # Ambil data pengguna
    pengguna = request.pengguna
    id_keluarga = pengguna.get_id_keluarga()
    id_sendiri = pengguna.id

    # Ambil semua data pengguna dengan id keluarga yang sama
    daftar_admin = Admin.objects.filter(_id_keluarga=id_keluarga)
    daftar_member = Member.objects.filter(_id_keluarga=id_keluarga)
    daftar_pengguna = list(daftar_admin) + list(daftar_member)

    # Render halaman daftar pengguna
    context = { 
        'daftar_pengguna': daftar_pengguna,
        'id_sendiri': id_sendiri,
        'pengguna': pengguna
    }
    return render(request, 'daftar_pengguna.html', context)

def detail_pengguna(request, id):
    if request.method == "GET":
        # Ambil data pengguna
        pengguna = request.pengguna
        id_sendiri = pengguna.id
        id_keluarga = pengguna.get_id_keluarga()

        # Coba cari target pengguna dari model Admin
        target_pengguna = Admin.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Jika tidak ditemukan di Admin, coba cari di Member
        if target_pengguna is None:
            target_pengguna = Member.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Jika tetap tidak ditemukan, tampilkan error
        if target_pengguna is None:
            return HttpResponseNotFound('Pengguna tidak ditemukan')

        # Render halaman detail pengguna
        context = {'pengguna': target_pengguna, 'id_sendiri': id_sendiri}
        return render(request, 'detail_pengguna.html', context)

    else:
        return HttpResponseForbidden('Tidak diizinkan.')

def post_tambah_pengguna(request):
    if request.method == "POST":
        # Ambil data pengguna
        pengguna = request.pengguna
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Tolak akses jika tidak memiliki izin
        nama_fitur = 'manajemen_pengguna'
        bisa_akses = pengguna.bisa_akses_fitur(nama_fitur)
        if not bisa_akses:
            return HttpResponseForbidden('Anda tidak memiliki akses fitur ini.')

        nama_admin = request.session.get('nama', '')
        email_pengguna_baru = request.POST.get('email').lower()
        peran_pengguna_baru = request.POST.get('peran')
        is_admin_pengguna_baru = peran_pengguna_baru == 'admin'
        id_keluarga = pengguna.get_id_keluarga()
        token = generate_token_login_unik(100)

        # Mulai validasi email pengguna baru
        # Jika email sudah terdaftar maka error
        if not is_email_tersedia(email_pengguna_baru):
            messages.error(request, "Email '" + email_pengguna_baru + "' sudah terdaftar")
            return redirect('daftar_pengguna')

        # Jika email sudah pernah dikirim namun calon pengguna baru belum login maka error
        is_email_pernah_dikirim = TokenLogin.objects.filter(email=email_pengguna_baru).exists()
        if is_email_pernah_dikirim:
            messages.error(request, "Email '" + email_pengguna_baru + "' sudah pernah dikirim sebelumnya")
            return redirect('daftar_pengguna')
        # Akhir validasi email pengguna baru

        # Mulai proses pengiriman email
        link_login = get_link_login(request, token)
        email_terkirim = kirim_mail_undangan(email_penerima=email_pengguna_baru, link_login=link_login, nama_admin=nama_admin, peran_pengguna=peran_pengguna_baru)

        # Jika email gagal terkirim maka error dan kembali ke halaman daftar pengguna
        if not email_terkirim:
          messages.error(request, 'Email gagal dikirim')
          return redirect('daftar_pengguna')
        
        messages.success(request, 'Email berhasil dikirim, menunggu pengguna untuk menerimanya')
        # Akhir proses pengiriman email

        # Menyimpan token
        data_token = TokenLogin(_id_keluarga=id_keluarga, email=email_pengguna_baru, is_admin=is_admin_pengguna_baru, _token=token)
        data_token.save()

        # Kembali ke halaman daftar pengguna
        return redirect('daftar_pengguna')
    else:
        return HttpResponseForbidden('Tidak diizinkan.')
    
    

def ubah_peran_pengguna(request, id, peran_baru):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        email = pengguna.email
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Tolak akses jika tidak memiliki izin
        nama_fitur = 'manajemen_pengguna'
        bisa_akses = pengguna.bisa_akses_fitur(nama_fitur)
        if not bisa_akses:
            return JsonResponse({
                'status': 'error',
                'message': 'Anda tidak memiliki akses fitur ini.'
            }, status=403)

        # Cari target pengguna dari Admin atau Member
        target_pengguna = Admin.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Debug
        print('target_pengguna', target_pengguna)
        print()

        if not target_pengguna:
            # Debug
            print('target_pengguna bukan admin, mencari di model Member...')
            print()
            target_pengguna = Member.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Jika tetap tidak ditemukan
        if not target_pengguna:
            return JsonResponse({
                'status': 'error',
                'message': 'Pengguna tidak ditemukan'
            }, status=404)

        peran_baru_low = peran_baru.lower()

        # Jika target pengguna adalah diri sendiri
        if target_pengguna.email.lower() == email.lower():
            return JsonResponse({
                'status': 'error',
                'message': 'Tidak dapat mengubah peran diri Anda sendiri'
            }, status=400)

        # Jika peran baru tidak valid
        if peran_baru_low not in ['admin', 'member']:
            messages.error(request, 'Peran baru tidak valid.')
            return redirect('daftar_pengguna')

        # Konversi ke boolean
        is_admin_baru = (peran_baru_low == 'admin')

        # Jika peran baru sama dengan peran lama
        if target_pengguna.is_admin == is_admin_baru:
            messages.error(request, f'{target_pengguna.nama} sudah menjadi {peran_baru_low} sebelumnya')
            return redirect('daftar_pengguna')

        # Simpan properti target pengguna sebelum dihapus
        target_nama = target_pengguna.nama
        target_email = target_pengguna.email
        target_password = target_pengguna.get_password()
        target_tanggal_lahir = target_pengguna.tanggal_lahir
        target_jenis_kelamin = target_pengguna.jenis_kelamin
        target_poin = target_pengguna.poin

        # Simpan dulu instance lama
        pengguna_lama = target_pengguna

        # Hapus pengguna lama
        # target_pengguna.delete()

        # Buat objek baru sesuai peran
        if is_admin_baru:
            pengguna_baru = Admin(
                nama=target_nama,
                email=target_email,
                tanggal_lahir=target_tanggal_lahir,
                jenis_kelamin=target_jenis_kelamin,
                is_admin=True,
                poin=target_poin
            )
        else:
            pengguna_baru = Member(
                nama=target_nama,
                email=target_email,
                tanggal_lahir=target_tanggal_lahir,
                jenis_kelamin=target_jenis_kelamin,
                is_admin=False,
                poin=target_poin
            )

        pengguna_baru.set_id_keluarga(id_keluarga)
        pengguna_baru.set_password(target_password)
        pengguna_baru.save()

        # Alihkan semua relasi Penugasan ke pengguna baru
        Penugasan.objects.filter(pengguna=pengguna_lama).update(pengguna=pengguna_baru)
        # Alihkan semua relasi TransaksiKeuangan ke pengguna baru
        TransaksiKeuangan.objects.filter(pengguna=pengguna_lama).update(pengguna=pengguna_baru)

        # Setelah semua relasi dialihkan, baru hapus pengguna lama
        pengguna_lama.delete()

        # Kembali ke halaman daftar pengguna
        return JsonResponse({
            'status': 'success',
            'message': f'{target_nama} telah berganti peran menjadi {peran_baru_low}'
        })
    else:
        return HttpResponseForbidden('Tidak diizinkan.')

# Daftar tugas
def daftar_tugas(request):
    pengguna = request.pengguna
    id_keluarga = pengguna.get_id_keluarga()
    is_admin = pengguna.is_admin

    daftar_admin = Admin.objects.filter(_id_keluarga=id_keluarga)
    daftar_member = Member.objects.filter(_id_keluarga=id_keluarga)
    daftar_pengguna = list(daftar_admin) + list(daftar_member)
    daftar_penugasan = []

    # Debug
    print('daftar_admin', list(daftar_admin.values()))
    print()
    print('daftar_member', list(daftar_member.values()))
    print()
    print('daftar_pengguna', daftar_pengguna)
    print()

    # Jika admin maka tampilkan semua tugas dalam satu keluarga
    if is_admin:
        print('Merupakan admin')
        print()
        daftar_penugasan = Penugasan.objects.filter(pengguna__in=daftar_pengguna)
    else:
        print('Merupakan member')
        print()
        daftar_penugasan = Penugasan.objects.filter(pengguna=pengguna)

    # Debug
    print('daftar_penugasan', daftar_penugasan)
    print()

    # Ambil semua objek Tugas yang ditugaskan kepada pengguna tertentu, berdasarkan ID tugas yang ada di dalam Penugasan.
    daftar_tugas = Tugas.objects.filter(id__in=daftar_penugasan.values_list('tugas_id', flat=True))
    
    for tugas in daftar_tugas:
        # Cek apakah pengguna termasuk dalam penugasan tugas ini
        penugasan_tugas_ini = daftar_penugasan.filter(tugas=tugas)

        # Debug
        print('penugasan_tugas_ini', list(penugasan_tugas_ini.values()), penugasan_tugas_ini.first().pengguna.email)
        print()
        
        # Hanya pengguna yang ditugaskan yang bisa menyelesaikan tugas
        # Debug
        print('pengguna.email', pengguna.email)
        print()
        print('list(penugasan.pengguna == pengguna for penugasan in penugasan_tugas_ini)', list(penugasan.pengguna == pengguna for penugasan in penugasan_tugas_ini))

        bisa_diselesaikan = False

        for penugasan in penugasan_tugas_ini:
            if penugasan.pengguna.id == pengguna.id:
                print('penugasan.pengguna', penugasan.pengguna)
                print(pengguna)
                print('penugasan.pengguna.id == pengguna.id', penugasan.pengguna.id == pengguna.id)
                bisa_diselesaikan = True
                print('tugas.bisa_diselesaikan', bisa_diselesaikan)
                break
        
        tugas.bisa_diselesaikan = bisa_diselesaikan
        
        print('bisa_diselesaikan', bisa_diselesaikan)
        print('tugas.bisa_diselesaikan 2', tugas.bisa_diselesaikan)
    
        print()

    # Debug
    print('daftar_tugas', list(daftar_tugas.values()))
    # print('bisa_menyelesaikan_tugas', 67 in list(bisa_menyelesaikan_tugas))
    # print(bisa_menyelesaikan_tugas[daftar_tugas.first().id])
    print()
    context = {
        'daftar_tugas': daftar_tugas,
        'daftar_pengguna': daftar_pengguna,
        'daftar_penugasan': daftar_penugasan,
        'pengguna': pengguna,
    }
    print('Render')
    print('-------------------------------')
    print()
    return render(request, 'daftar_tugas.html', context)

# NOTE: Lihat struktur database pada "Family Organizer.png"
def post_tambah_tugas(request):
    if request.method == 'POST':
        # Ambil data pengguna
        pengguna = request.pengguna
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Tolak akses untuk non-admin
        if not is_admin:
            return HttpResponseForbidden('Anda tidak memiliki akses fitur ini karena Anda bukan admin')

        # Ambil data dari formulir
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        tenggat = request.POST.get('tenggat')
        poin = request.POST.get('poin')
        list_id_pelaku_tugas = request.POST.getlist('ditugaskan_kepada')

        tenggat_naive = datetime.fromisoformat(tenggat)
        tenggat = timezone.make_aware(tenggat_naive)

        # Mulai validasi formulir
        errors = []

        if not judul or judul.strip() == "":
            errors.append("Judul tidak boleh kosong.")

        if not deskripsi or deskripsi.strip() == "":
            errors.append("Deskripsi tidak boleh kosong.")

        if not request.POST.get('tenggat'):
            errors.append("Tenggat waktu harus diisi.")
        else:
            try:
                if tenggat < timezone.now():
                    errors.append("Tenggat waktu tidak boleh di masa lalu.")
            except ValueError:
                errors.append("Format tenggat waktu tidak valid.")

        if not poin or not poin.isdigit() or int(poin) < 0:
            errors.append("Poin harus berupa angka bulat positif.")

        if not list_id_pelaku_tugas:
            errors.append("Setidaknya satu pelaku tugas harus dipilih.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('daftar_tugas')
        # Akhir validasi formulir

        # Ubah semua value menjadi integer
        list_id_pelaku_tugas_int = [int(id) for id in list_id_pelaku_tugas]

        # Menambahkan tugas ke dalam tabel Tugas
        poin_int = int(poin)
        tugas_baru = Tugas(_id_keluarga=id_keluarga, judul=judul, deskripsi=deskripsi, poin=poin_int, tenggat_waktu=tenggat)
        tugas_baru.save()

        # Looping untuk menambahkan "siapa saja yang mengerjakan apa saja" satu-persatu
        for id_pelaku in list_id_pelaku_tugas_int:
            pelaku = Admin.objects.filter(id=id_pelaku, _id_keluarga=id_keluarga).first()
            if not pelaku:
                pelaku = Member.objects.filter(id=id_pelaku, _id_keluarga=id_keluarga).first()

            # Jika pelaku tetap tidak ditemukan
            if pelaku is None:
                messages.error(request, 'Terjadi kesalahan saat menambahkan tugas. Pengguna yang ditugaskan ada yang tidak ditemukan.')
                return redirect('daftar_tugas')

            # Menyimpan data penugasan
            peran_pelaku = 'admin' if pelaku.is_admin else 'member'
            penugasan = Penugasan(pengguna=pelaku, tugas=tugas_baru, peran=peran_pelaku)
            penugasan.save()

        # Kembali ke halaman daftar tugas
        messages.success(request, 'Tugas berhasil ditambahkan.')
        return redirect('daftar_tugas')

    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def put_status_tugas(request, id):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()

        # Jika pengguna ditugaskan pada tugas ini, 

        # Mencari tugas
        tugas = Tugas.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Apabila tugas tidak ada, menampilkan error
        if tugas is None:
            messages.error(request, 'Tugas tidak ditemukan')
            return redirect('daftar_tugas')
        
        poin_tugas = tugas.poin
        
        # Cek apakah tugas melewati deadline. Jika ya, poin tidak akan ditambahkan kepada pengguna namun tetap dihapus tugasnya
        if tugas.is_telat():
            # Hapus tugas dari database
            tugas.delete()
            # Kembali ke halaman daftar tugas
            messages.error(request, 'Tugas terlambat diselesaikan. Tidak ada tambahan poin untuk Anda.')
            return redirect('daftar_tugas')

        # Tambah poin pengguna apabila tidak melewati deadline
        pengguna.poin = pengguna.poin + poin_tugas
        pengguna.save()

        # Hapus tugas dari database
        tugas.delete()

        # Kembali ke halaman daftar tugas
        messages.success(request, 'Tugas berhasil diselesaikan.' + "+" + str(poin_tugas) + " poin untuk Anda.")
        return redirect('daftar_tugas')
    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def delete_tugas(request, id):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()

        # Mencari tugas
        tugas = Tugas.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Apabila tugas tidak ada, menampilkan error
        if tugas is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Tugas Tidak Ditemukan'
            }, status=400)

        # Hapus tugas dari database
        tugas.delete()

        # Kembali ke halaman daftar tugas
        return JsonResponse({
                'status': 'success',
                'message': 'Tugas Berhasil Dihapus'
            })
    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def detail_tugas(request, id):
    if request.method == 'GET':
        pengguna = request.pengguna
        # Ambil data tugas
        target_tugas = Tugas.objects.filter(id=id).first()

        # Apabila tidak ditemukan maka error
        if target_tugas is None:
            return HttpResponseNotFound('Tugas tidak ditemukan')

        # Ambil semua Penugasan yang berelasi dengan tugas tersebut
        penugasan_tugas = Penugasan.objects.filter(tugas=target_tugas)

        # Ambil semua ID pengguna dari hasil penugasan
        list_pengguna_id = penugasan_tugas.values_list('pengguna_id', flat=True)

        # Cari pengguna di Admin dan Member
        list_pelaku_admin = Admin.objects.filter(id__in=list_pengguna_id)
        list_pelaku_member = Member.objects.filter(id__in=list_pengguna_id)

        # Gabungkan hasilnya jadi satu list
        list_pelaku_tugas = list(list_pelaku_admin) + list(list_pelaku_member)

        # Buat string nama-nama pelaku tugas
        ditugaskan_kepada = ', '.join([pelaku.nama for pelaku in list_pelaku_tugas])

        # Render halaman
        context = {
            'tugas': target_tugas,
            'ditugaskan_kepada': ditugaskan_kepada,
            'pengguna': pengguna
        }
        return render(request, 'detail_tugas.html', context)

    else:
        return HttpResponseForbidden("Tidak diizinkan.")

# Input pemasukan / pengeluaran
def input_keuangan(request):
    context = {}
    if request.method == 'POST':
        # proses input keuangan
        return redirect('beranda')
    return render(request, 'input_keuangan.html', context)

# Statistik keuangan atau tugas
def statistik(request):
    context = {}
    # bisa ditambahkan statistik keuangan atau tugas
    return render(request, 'statistik.html', context)

# Daftar stok barang
def daftar_barang(request):
    pengguna = request.pengguna
    id_keluarga = pengguna.get_id_keluarga()
    # Ambil barang dari database
    daftar_barang = Stok.objects.filter(_id_keluarga=id_keluarga)
    context = {
        'daftar_barang': daftar_barang,
    }
    return render(request, 'daftar_barang.html', context)

def post_tambah_barang(request):
    if request.method == "POST":
        # Ambil data pengguna
        pengguna = request.pengguna
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil data formulir
        nama = request.POST.get('nama')
        jumlah = request.POST.get('jumlah')
        satuan = request.POST.get('satuan')
        interval_habis = request.POST.get('interval_habis')

        # Mulai validasi formulir
        errors = []

        if not nama or nama.strip() == "":
            errors.append("Nama barang tidak boleh kosong.")
        
        if not jumlah or jumlah.strip() == "":
            errors.append("Jumlah barang tidak boleh kosong.")

        if not jumlah.isdigit():
            errors.append('Jumlah barang harus berupa angka dan harus lebih dari nol.')

        if not satuan or satuan.strip() == '':
            errors.append('Satuan tidak boleh kosong')

        if not interval_habis or interval_habis.strip() == '':
            errors.append('Interval habis tidak boleh kosong')

        if not interval_habis.isdigit():
            errors.append('Interval habis harus berupa angka dan harus lebih dari nol.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('daftar_barang')
        # Akhir validasi formulir

        # Ubah menjadi integer dan float
        jumlah_float = float(jumlah)
        interval_habis_int = int(interval_habis)

        # Simpan ke database
        barang = Stok(nama=nama, jumlah=jumlah_float, satuan=satuan, interval_habis=interval_habis_int)
        barang.set_id_keluarga(id_keluarga)
        barang.save()

        # Kembali ke halaman daftar barang
        messages.success(request, 'Barang berhasil ditambahkan.')
        return redirect('daftar_barang')
    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def delete_barang(request, id):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()
        is_admin = pengguna.is_admin

        # Mencari barang
        barang = Stok.objects.filter(id=id, _id_keluarga=id_keluarga).first()

        # Apabila barang tidak ada, menampilkan error
        if barang is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Barang tidak ditemukan'
            })
            # messages.error(request, 'Barang tidak ditemukan')
            # return redirect('daftar_barang')

        # Hapus barang dari database
        barang.delete()

        # Kembali ke halaman daftar barang
        return JsonResponse({
                'status': 'success',
                'message': 'Barang Berhasil Dihapus'
            })
        return redirect('daftar_barang')
    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def detail_barang(request, id):
    if request.method == "GET":
        barang = Stok.objects.filter(id=id).first()

        if barang is None:
            return HttpResponseNotFound('Barang tidak ditemukan')
        
        context = { 'barang': barang }
        return render(request, 'detail_barang.html', context)
    else:
        return HttpResponseForbidden('Tidak diizinkan.')
    
def input_pemasukan(request):
    pengguna = request.pengguna
    id_keluarga = pengguna.get_id_keluarga()

    # Ambil semua pengguna dari keluarga ini (baik admin maupun member)
    daftar_admin = Admin.objects.filter(_id_keluarga=id_keluarga)
    daftar_member = Member.objects.filter(_id_keluarga=id_keluarga)
    daftar_pengguna = list(daftar_admin) + list(daftar_member)

    context = { 'daftar_pengguna': daftar_pengguna }
    return render(request, 'input_pemasukan.html', context)

def input_pengeluaran(request):
    pengguna = request.pengguna
    id_keluarga = pengguna.get_id_keluarga()

    # Ambil semua pengguna dari keluarga ini (baik admin maupun member)
    daftar_admin = Admin.objects.filter(_id_keluarga=id_keluarga)
    daftar_member = Member.objects.filter(_id_keluarga=id_keluarga)
    daftar_pengguna = list(daftar_admin) + list(daftar_member)

    context = { 'daftar_pengguna': daftar_pengguna }
    return render(request, 'input_pengeluaran.html', context)


def post_tambah_pemasukan(request):
    if request.method == 'POST':
        # Ambil data pengguna
        pengguna = request.pengguna
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil data dari formulir
        nama = request.POST.get('nama')
        nominal = request.POST.get('nominal')
        tanggal = request.POST.get('tanggal')
        id_pelaku_transaksi = request.POST.get('pelaku_transaksi')

        # Mulai validasi formulir
        errors = []

        if not nama or nama.strip() == "":
            errors.append("Nama tidak boleh kosong.")

        if not nominal or nominal.strip() == "":
            errors.append("Nominal tidak boleh kosong.")
        elif not nominal.isdigit() or int(nominal) <= 0:
            errors.append("Nominal harus berupa angka dan harus lebih dari nol.")

        if not id_pelaku_transaksi or id_pelaku_transaksi.strip() == "":
            errors.append("Harus memilih satu pelaku transaksi.")

        if not tanggal:
            errors.append("Tanggal transaksi harus diisi.")
        else:
            try:
                tanggal_naive = datetime.fromisoformat(tanggal)
                tanggal = timezone.make_aware(tanggal_naive)
                if tanggal > timezone.now():
                    errors.append("Tanggal transaksi tidak boleh di masa depan.")
            except ValueError:
                errors.append("Format tanggal transaksi tidak valid.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('input_pemasukan')
        # Akhir validasi formulir

        # Ubah ID pelaku ke integer
        id_pelaku_transaksi_int = int(id_pelaku_transaksi)

        # Ambil pelaku transaksi dari Admin atau Member
        pelaku = Admin.objects.filter(id=id_pelaku_transaksi_int, _id_keluarga=id_keluarga).first()
        if pelaku is None:
            pelaku = Member.objects.filter(id=id_pelaku_transaksi_int, _id_keluarga=id_keluarga).first()

        if pelaku is None:
            messages.error(request, 'Pelaku transaksi tidak ditemukan')
            return redirect('input_pemasukan')

        # Tambahkan pemasukan ke tabel TransaksiKeuangan
        nominal_float = float(nominal)
        jenis = 'pemasukan'
        pemasukan_baru = TransaksiKeuangan(
            _id_keluarga=id_keluarga,
            pengguna=pelaku,
            nama=nama,
            nominal=nominal_float,
            tanggal_transaksi=tanggal,
            jenis=jenis
        )
        pemasukan_baru.save()

        # Redirect ke halaman input pemasukan
        messages.success(request, 'Transaksi berhasil ditambahkan')
        return redirect('input_pemasukan')

    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def post_tambah_pengeluaran(request):
    if request.method == 'POST':
        # Ambil data pengguna
        pengguna = request.pengguna
        is_admin = pengguna.is_admin
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil data dari formulir
        nama = request.POST.get('nama')
        nominal = request.POST.get('nominal')
        tanggal = request.POST.get('tanggal')
        id_pelaku_transaksi = request.POST.get('pelaku_transaksi')

        # Mulai validasi formulir
        errors = []

        if not nama or nama.strip() == "":
            errors.append("Nama tidak boleh kosong.")

        if not nominal or nominal.strip() == "":
            errors.append("Nominal tidak boleh kosong.")
        elif not nominal.isdigit() or int(nominal) <= 0:
            errors.append("Nominal harus berupa angka dan harus lebih dari nol.")

        if not id_pelaku_transaksi or id_pelaku_transaksi.strip() == "":
            errors.append("Harus memilih satu pelaku transaksi.")

        if not tanggal:
            errors.append("Tanggal transaksi harus diisi.")
        else:
            try:
                tanggal_naive = datetime.fromisoformat(tanggal)
                tanggal = timezone.make_aware(tanggal_naive)
                if tanggal > timezone.now():
                    errors.append("Tanggal transaksi tidak boleh di masa depan.")
            except ValueError:
                errors.append("Format tanggal transaksi tidak valid.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('input_pengeluaran')
        # Akhir validasi formulir

        # Ubah ID pelaku ke integer
        id_pelaku_transaksi_int = int(id_pelaku_transaksi)

        # Ambil pelaku transaksi dari Admin atau Member
        pelaku = Admin.objects.filter(id=id_pelaku_transaksi_int, _id_keluarga=id_keluarga).first()
        if pelaku is None:
            pelaku = Member.objects.filter(id=id_pelaku_transaksi_int, _id_keluarga=id_keluarga).first()

        if pelaku is None:
            messages.error(request, 'Pelaku transaksi tidak ditemukan')
            return redirect('input_pengeluaran')

        # Tambahkan pengeluaran ke tabel TransaksiKeuangan
        nominal_float = float(nominal)
        jenis = 'pengeluaran'
        pengeluaran_baru = TransaksiKeuangan(
            _id_keluarga=id_keluarga,
            pengguna=pelaku,
            nama=nama,
            nominal=nominal_float,
            tanggal_transaksi=tanggal,
            jenis=jenis
        )
        pengeluaran_baru.save()

        # Redirect ke halaman input pengeluaran
        messages.success(request, 'Transaksi berhasil ditambahkan')
        return redirect('input_pengeluaran')

    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def get_statistik_keuangan(request):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil semua transaksi keuangan milik keluarga ini
        list_transaksi = TransaksiKeuangan.objects.filter(_id_keluarga=id_keluarga)

        # Deklarasi dictionary kosong
        data_pemasukan = defaultdict(float)
        data_pengeluaran = defaultdict(float)

        # Looping untuk menambahkan setiap transaksi ke dictionary
        for transaksi in list_transaksi:
            # Ubah tanggal menjadi format string yyyy-mm-dd
            tanggal_str = timezone.localtime(transaksi.tanggal_transaksi).strftime('%Y-%m-%d')
            # Pisahkan antara transaksi pemasukan dan pengeluaran
            if transaksi.jenis == 'pemasukan':
                data_pemasukan[tanggal_str] += transaksi.nominal
            elif transaksi.jenis == 'pengeluaran':
                data_pengeluaran[tanggal_str] += transaksi.nominal
        
        # Ubah dictionary menjadi set
        # 
        # Contoh dictionary:
        # data_contoh = {
        #     '2025-05-01': 10000,
        #     '2025-05-02': 12000,
        #     '2025-05-03': 15000,
        #     '2025-05-04': 18000,
        # }
        # 
        # Contoh setelah diubah menjadi set:
        # set_data_contoh = { '2025-05-01', '2025-05-02', '2025-05-03', '2025-05-04' }
        set_tanggal_pemasukan = set(data_pemasukan)
        set_tanggal_pengeluaran = set(data_pengeluaran)

        # Gabungkan tanggal menggunakan operator union "|"
        # Contoh saat union:
        # { '2025-05-01', '2025-05-02' } | { '2025-05-02', '2025-05-03' }
        # Contoh setelah union:
        # { '2025-05-01', '2025-05-02', '2025-05-03' }
        set_tanggal_gabungan = set_tanggal_pemasukan | set_tanggal_pengeluaran

        # Sortir tanggal dan jadikan list
        semua_tanggal = sorted(set_tanggal_gabungan)

        # Masukkan nominal transaksi yang telah diurutkan berdasarkan tanggal ke dalam list
        semua_pemasukan = []
        semua_pengeluaran = []
        semua_selisih = []
        for tgl in semua_tanggal:
            # Masukkan nominal pemasukan/pengeluaran ke dalam list, apabila pada tanggal tertentu tidak ada pemasukan/pengeluaran maka nominalnya ditulis 0
            pemasukan = data_pemasukan.get(tgl, 0)
            pengeluaran = data_pengeluaran.get(tgl, 0)
            selisih = pemasukan - pengeluaran
            semua_pemasukan.append(pemasukan)
            semua_pengeluaran.append(pengeluaran)
            semua_selisih.append(selisih)

        return JsonResponse({
            'tanggal': semua_tanggal,
            'pemasukan': semua_pemasukan,
            'pengeluaran': semua_pengeluaran,
            'selisih': semua_selisih
        })
    else:
        return HttpResponseForbidden("Tidak diizinkan.")
    
def get_statistik_poin_kontribusi(request):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil semua anggota keluarga dari Admin dan Member
        admin_list = Admin.objects.filter(_id_keluarga=id_keluarga)
        member_list = Member.objects.filter(_id_keluarga=id_keluarga)

        # Gabungkan keduanya
        list_pengguna = list(admin_list) + list(member_list)

        # Ambil list nama dan list poin
        semua_nama = []
        semua_poin = []

        for pengguna in list_pengguna:
            semua_nama.append(pengguna.nama)
            semua_poin.append(pengguna.poin)

        return JsonResponse({
            'nama': semua_nama,
            'poin': semua_poin
        })

    else:
        return HttpResponseForbidden("Tidak diizinkan.")

def histori_keuangan(request):
    if request.method == 'GET':
        # Ambil data pengguna
        pengguna = request.pengguna
        id_keluarga = pengguna.get_id_keluarga()

        # Ambil semua transaksi milik keluarga, termasuk data pengguna (pelaku transaksi)
        list_transaksi = TransaksiKeuangan.objects.filter(
            _id_keluarga=id_keluarga
        ).select_related('pengguna')

        # Struktur: { '2025-05-01': [transaksi1, transaksi2, ...] }
        histori_dict = defaultdict(list)

        for transaksi in list_transaksi:
            tanggal_str = timezone.localtime(transaksi.tanggal_transaksi).strftime('%Y-%m-%d')
            histori_dict[tanggal_str].append({
                'nama': transaksi.nama,
                'nominal': transaksi.nominal,
                'pelaku_transaksi': transaksi.pengguna, # pengguna yang membuat transaksi
                'jenis': transaksi.jenis  
            })

        # Konversi ke list dan urutkan tanggalnya
        histori_keuangan = [
            {
                'tanggal': format_tanggal_indonesia(tanggal),
                'transaksi': transaksi_list
            }
            for tanggal, transaksi_list in sorted(histori_dict.items())
        ]

        context = {
            'histori_keuangan': histori_keuangan
        }

        return render(request, 'histori_keuangan.html', context)
    else:
        return HttpResponseForbidden("Tidak diizinkan.")
    