# 📂 Cara Menjalankan Aplikasi Family Organizer (Django)

## ✅ Persyaratan Awal

Pastikan di laptop/komputer sudah terinstall:

- Python (versi 3.8+)
- pip
- (Opsional) Virtual Environment

---

## 🔧 Langkah Menjalankan Aplikasi

### 1. Buka proyek melalui Visual Studio Code lalu buka terminal

### 2. Aktifkan virtual environment

**Jika folder `venv/` ada:**

```bash
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

**Jika belum ada:** bisa membuat baru:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Install library yang dibutuhkan

```bash
pip install -r requirements.txt
```

### 4. Jalankan migrasi database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Jalankan server

```bash
python manage.py runserver
```

Jika muncul error seperti:

```
Error: You don't have permission to access that port.
```

Gunakan port lain. Contoh: 8080:

```bash
python manage.py runserver 8080
```

### 6. Akses aplikasi

Buka browser dan kunjungi:

```sh
http://127.0.0.1:8000/
```

Atau

```sh
http://127.0.0.1:8080/
```
