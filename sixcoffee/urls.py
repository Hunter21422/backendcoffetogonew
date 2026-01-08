from django.http import JsonResponse
from django.contrib import admin
from django.conf import settings
from django.urls import path, include  # ← ВОТ ЗДЕСЬ ДОБАВЬ path, если его нет!
from django.conf.urls.static import static
def api_root(request):
    return JsonResponse({
        "status": "online",
        "message": "Coffee Loyalty API",
        "endpoints": {
            "telegram_auth": "/telegram-auth/",
            "me": "/me/",
            "user_profile": "/user/profile/",
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path(" ", include("Loyality.urls")),
]



