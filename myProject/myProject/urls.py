#urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static
from mySplitterApp.views import separate_audio

urlpatterns = [
    path('admin/', admin.site.urls),
    path('separate/', separate_audio, name='separate_audio'),
    # Removed the queue_status URL pattern
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
