def set_sesi_pengguna(request, id_keluarga: str, nama: str, email: str, password: str, tanggal_lahir: str, jenis_kelamin: str, is_admin: str, poin: str):
    request.session['id_keluarga'] = id_keluarga
    request.session['nama'] = nama
    request.session['email'] = email
    request.session['password'] = password
    request.session['tanggal_lahir'] = tanggal_lahir
    request.session['jenis_kelamin'] = jenis_kelamin
    request.session['is_admin'] = is_admin
    request.session['poin'] = poin