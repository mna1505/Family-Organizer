def get_link_login(request, token):
    return request.scheme + '://' + request.get_host() + '/login_baru/?token=' + token