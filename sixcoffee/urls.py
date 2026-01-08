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
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path(" ", include("Loyality.urls")),
]


