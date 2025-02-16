from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import ShortLinkRedirectView


urlpatterns = [
    path(
        's/<str:short_link>/',
        ShortLinkRedirectView.as_view(),
        name='short_link_redirect'
    ),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
