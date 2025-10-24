import fnmatch
from django.shortcuts import redirect
from django.contrib import messages
from ..models import Admin, Member

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = ['/', '/admin/*', '/index/', '/signup/', '/post_signup/', '/login_baru/', '/login/', '/post_login/', '/post_login_baru/', '/logout/', '/generate_data_dummy/']

    def is_path_allowed(self, path):
        return any(fnmatch.fnmatch(path, pattern) for pattern in self.allowed_paths)

    def __call__(self, request):
        if self.is_path_allowed(request.path):
            return self.get_response(request)
        
        email = request.session.get('email')
        password = request.session.get('password')
        is_admin = request.session.get('is_admin')

        if email is None or password is None:
            messages.error(request, 'Login untuk melanjutkan')
            return redirect('login')
        
        pengguna = None
        if int(is_admin) == 1:
            pengguna = Admin.objects.filter(email=email).first()
        else:
            pengguna = Member.objects.filter(email=email).first()


        if pengguna is None or pengguna.get_password() != password:
            messages.error(request, 'Login untuk melanjutkan...')
            return redirect('login')

        request.pengguna = pengguna

        return self.get_response(request)