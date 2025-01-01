from django.shortcuts import redirect

class RestrictSecretaryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.user_type == 'secretary':
            # Sadece sekreterlerin erişimini kısıtla
            allowed_paths = ['/profile/', '/login/', '/logout/', '/']
            if request.path not in allowed_paths:
                return redirect('index')
        return self.get_response(request)
