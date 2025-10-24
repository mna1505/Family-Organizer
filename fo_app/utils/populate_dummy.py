import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from fo_app.models import Admin, Member, TokenLogin, Tugas, Penugasan, Stok, TransaksiKeuangan

fake = Faker()

def generate_dummy_family_data(id_keluarga=1001, jumlah_member=2):
    now = timezone.now()

    # 1. Admin
    admin_nama = fake.name()
    admin_email = fake.email()
    admin = Admin.objects.create(
        id_keluarga=id_keluarga,
        nama=admin_nama,
        email=admin_email,
        password='admin123',
        tanggal_lahir=fake.date_of_birth(minimum_age=30, maximum_age=50),
        jenis_kelamin=random.choice([True, False]),
        is_admin=True,
        poin=random.randint(50, 100)
    )

    TokenLogin.objects.create(
        id_keluarga=id_keluarga,
        email=admin_email,
        is_admin=True,
        token=fake.uuid4()
    )

    # 2. Members
    members = []
    for _ in range(jumlah_member):
        nama = fake.name()
        email = fake.email()
        member = Member.objects.create(
            id_keluarga=id_keluarga,
            nama=nama,
            email=email,
            password='member123',
            tanggal_lahir=fake.date_of_birth(minimum_age=10, maximum_age=25),
            jenis_kelamin=random.choice([True, False]),
            poin=random.randint(10, 80)
        )
        TokenLogin.objects.create(
            id_keluarga=id_keluarga,
            email=email,
            is_admin=False,
            token=fake.uuid4()
        )
        members.append(member)

    # 3. Tugas dan penugasan
    for i in range(2):
        judul = f"Tugas: {fake.word().capitalize()} Rumah"
        tugas = Tugas.objects.create(
            id_keluarga=id_keluarga,
            judul=judul,
            deskripsi=fake.sentence(nb_words=10),
            status=random.choice(['belum_selesai', 'selesai']),
            poin=random.randint(5, 20),
            tenggat_waktu=now + timedelta(days=random.randint(1, 5))
        )

        Penugasan.objects.create(pengguna=admin, tugas=tugas, peran='admin')
        for member in members:
            Penugasan.objects.create(pengguna=member, tugas=tugas, peran='member')

    # 4. Stok
    for _ in range(3):
        nama_barang = fake.word().capitalize()
        Stok.objects.create(
            id_keluarga=id_keluarga,
            nama=nama_barang,
            jumlah=round(random.uniform(1.0, 10.0), 2),
            satuan=random.choice(['kg', 'liter', 'buah']),
            interval_habis=random.randint(7, 30)
        )

    # 5. Transaksi Keuangan
    transaksi_users = [admin] + members
    for _ in range(4):
        pengguna = random.choice(transaksi_users)
        jenis = random.choice(['pemasukan', 'pengeluaran'])
        TransaksiKeuangan.objects.create(
            id_keluarga=id_keluarga,
            pengguna=pengguna,
            nama=fake.bs().capitalize(),
            nominal=round(random.uniform(10000, 250000), 2),
            tanggal_transaksi=now - timedelta(days=random.randint(0, 10)),
            jenis=jenis
        )

    print(f"✅ Dummy data untuk keluarga {id_keluarga} berhasil dibuat dengan {jumlah_member} member.")
