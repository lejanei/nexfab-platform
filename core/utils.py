def get_company(request):
    """Retorna a empresa do usuário logado."""
    return request.user.userprofile.company