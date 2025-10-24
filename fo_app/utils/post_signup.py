from ..models import AbstrakPengguna
import random

def generate_id_keluarga():
    return random.randint(100000, 999999)

def is_id_keluarga_tersedia(id_keluarga):
    return not AbstrakPengguna.objects.filter(_id_keluarga=id_keluarga).exists()

def generate_id_keluarga_unik():
    id_keluarga = generate_id_keluarga()

    while not is_id_keluarga_tersedia(id_keluarga):
        id_keluarga = generate_id_keluarga()
    
    return id_keluarga

def is_email_tersedia(email):
    return not AbstrakPengguna.objects.filter(email=email).exists()