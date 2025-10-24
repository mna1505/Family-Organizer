import string
import random
from ..models import TokenLogin

def generate_token_login(length):
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    token = ''.join(random.choices(characters, k=length))
    return token

def is_token_login_tersedia(token):
    return not TokenLogin.objects.filter(_token=token).exists()

def generate_token_login_unik(length):
    token = generate_token_login(length)

    while not is_token_login_tersedia(token):
        token = generate_token_login(length)
    
    return token
