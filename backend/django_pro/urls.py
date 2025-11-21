from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('about/', include('about.urls')),
    path('booking/', include('booking.urls')),
    path('catalog/', include('catalog.urls')),
    path('masters/', include('masters.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    # Статические файлы из всех папок STATICFILES_DIRS
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0]
    )

    # Медиа файлы
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
