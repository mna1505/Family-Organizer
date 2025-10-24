import datetime

def format_tanggal_indonesia(tanggal_str):
    # Daftar nama hari dan bulan dalam Bahasa Indonesia
    nama_hari = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    nama_bulan = [
        '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]

    try:
        # Parsing string tanggal
        tanggal = datetime.datetime.strptime(tanggal_str.strip(), "%Y-%m-%d")
        hari = nama_hari[tanggal.weekday()]      # weekday: 0=Senin, ..., 6=Minggu
        tanggal_angka = tanggal.day
        bulan = nama_bulan[tanggal.month]
        tahun = tanggal.year

        return f"{hari}, {tanggal_angka} {bulan} {tahun}"
    except ValueError:
        print("Tanggal tidak valid atau salah format (gunakan YYYY-MM-DD).")
        return tanggal_str