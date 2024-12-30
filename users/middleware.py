# from datetime import datetime
# from users.models import UserActivityLog
#
# class UserActivityMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#
#         # Sadece oturum açmış kullanıcılar için kaydet
#         if request.user.is_authenticated:
#             action = None
#
#             # Örnek CRUD eylemleri
#             if request.method == "POST":
#                 action = f"POST isteği yapıldı: {request.path}"
#             elif request.method == "GET":
#                 action = f"Sayfa ziyaret edildi: {request.path}"
#
#             # Sadece belirli yolları kaydetmek isterseniz
#             # Örneğin: Profil güncelleme veya belirli bir yol
#             if request.path.startswith("/profile"):
#                 action = f"Profil sayfasında işlem yapıldı: {request.path}"
#
#             if action:
#                 UserActivityLog.objects.create(user=request.user, action=action, timestamp=datetime.now())
#
#         return response
