from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.http import JsonResponse

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
    path('', api_root, name='api-root'),  # ← root-эндпоинт
    path('admin/', admin.site.urls),
    path("", include("Loyality.urls")),    # ← без пробела!
]

# Медиа в DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



