from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.colortest.admin_site if hasattr(admin, 'site') and hasattr(admin.site, 'colortest') else admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('shop.urls', namespace='shop')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
