from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ImproperlyConfigured
from smtplib import SMTPException
from django.http import HttpResponse

""" 
Isi Email:
- Subject
- Pesan dinamis (dapat dikustomisasi: peran, )
- Link login
"""

def get_isi_email(link_login, nama_admin, peran_pengguna):
    return f'''<!DOCTYPE html>
<html>
<head>
  <style>
    .email-container {{
      font-family: Arial, sans-serif;
      padding: 20px;
      background-color: #f4f4f4;
      color: #333;
    }}
    .email-box {{
      background-color: #ffffff;
      border-radius: 8px;
      padding: 30px;
      text-align: center;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }}
    .btn {{
      display: inline-block;
      margin-top: 20px;
      padding: 12px 25px;
      background-color: #28a745;
      color: white;
      text-decoration: none;
      font-weight: bold;
      border-radius: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 12px;
      color: #888;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="email-box">
      <h2>Undangan Login ke Family Organizer</h2>
      <p>Anda telah diundang sebagai <strong>{peran_pengguna}</strong> oleh Admin bernama {nama_admin}.</p>
      <p>Silakan klik tombol di bawah ini untuk login ke aplikasi dan mengatur kata sandi pertama Anda:</p>
      <a href="{link_login}" class="btn">Masuk ke Aplikasi</a>
      <p class="footer">Jika Anda tidak mengenal pengirim, abaikan email ini.</p>
    </div>
  </div>
</body>
</html>'''

def kirim_mail_undangan(email_penerima, link_login, nama_admin, peran_pengguna):
    subject = 'Undangan Bergabung ke Aplikasi Family Organizer'
    pesan = 'Silakan klik link berikut untuk aktivasi.'
    pesan_html = get_isi_email(link_login, nama_admin, peran_pengguna)
    pengirim = 'familyorganizerteam@gmail.com'

    try:
        send_mail(subject=subject, message=pesan, from_email=pengirim, recipient_list=[email_penerima], fail_silently=False, html_message=pesan_html)
        return True
    except BadHeaderError:
        # Header email tidak valid
        print("Header email tidak valid.")
        return False
    except SMTPException as e:
        # Kesalahan pada koneksi SMTP atau server email
        print(f"Gagal mengirim email karena SMTP error: {e}")
        return False
    except ImproperlyConfigured as e:
        # Kesalahan konfigurasi EMAIL di settings.py
        print(f"Konfigurasi email salah: {e}")
        return False
    except Exception as e:
        # Penanganan error umum
        print(f"Terjadi kesalahan saat mengirim email: {e}")
        return False
    
def kirim_email_pengingat_stok(pengguna, stok):
    subjek = f"Pengingat: Stok '{stok.nama}' Akan Habis"
    isi_pesan = (
        f"Hai {pengguna.nama},\n\n"
        f"Stok '{stok.nama}' perlu dicek. Berdasarkan interval habis ({stok.interval_habis} hari), "
        f"stok seharusnya sudah dicek kembali.\n\n"
        "Segera periksa dan perbarui jika diperlukan.\n\n"
        "Terima kasih,\nSistem Manajemen Keluarga"
    )
    dari_email = 'familyorganizerteam@gmail.com'
    kepada = [pengguna.email]

    try:
        send_mail(
          subject=subjek,
          message=isi_pesan,
          from_email=dari_email,
          recipient_list=kepada,
          fail_silently=False,
        )
        return True
    except BadHeaderError:
        # Header email tidak valid
        print("Header email tidak valid.")
        return False
    except SMTPException as e:
        # Kesalahan pada koneksi SMTP atau server email
        print(f"Gagal mengirim email karena SMTP error: {e}")
        return False
    except ImproperlyConfigured as e:
        # Kesalahan konfigurasi EMAIL di settings.py
        print(f"Konfigurasi email salah: {e}")
        return False
    except Exception as e:
        # Penanganan error umum
        print(f"Terjadi kesalahan saat mengirim email: {e}")
        return False