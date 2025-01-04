from django.shortcuts import redirect


class RestrictSecretaryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.user_type == 'secretary':
            # Sadece sekreterlerin erişimini kısıtla
            allowed_paths = ['/profile/', '/login/', '/logout/', '/', 'index/', '/secretary/', '/list_notes/',
                             '/add_note/', '/api/calendar-events/', '/calendar/', '/dashboard/', '/how-to-use/',
                             '/version-info/', '/get-notes/', '/notes/', '/notes/add/', '/notes/filter/', '/notes/edit/<int:note_id>/']
            if request.path not in allowed_paths:
                return redirect('index')
        return self.get_response(request)
