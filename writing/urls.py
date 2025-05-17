from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='core/home.html'), name='home'),
    path('', include('users.urls')),
    path('', include('core.urls')),
    path('ai/', include('ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
