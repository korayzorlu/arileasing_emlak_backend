from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


# Reads straight off disk instead of going through Django's template loader — the
# project's TEMPLATES["DIRS"] isn't configured for the root templates/ folder, and this
# static page has no context to render anyway.
def account_deletion(request):
    html = (settings.BASE_DIR / 'templates' / 'account_deletion.html').read_text(encoding='utf-8')
    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Public, unauthenticated — linked from the Google Play "Data safety" account
    # deletion field, so it must be reachable without the app installed.
    # Lives under /api/ specifically because nginx's site config (nginx/conf.d/emlak.conf)
    # only proxies /admin/ and /api/ to the Django container; anything else falls through
    # to an unrelated, empty static root and 404s.
    path('api/hesap-silme/', account_deletion, name='account-deletion'),

    path('api/auth/', include('accounts.urls')),
    path('api/properties/', include('properties.urls')),
    path('api/whatsapp/', include('whatsapp.urls')),
    path('api/brochure/', include('brochure.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)