"""
URL configuration for registro_control_eventos project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Redirect raíz a dashboard
    path('', RedirectView.as_view(pattern_name='dashboard:index', permanent=False)),
    
    # Apps
    path('usuarios/', include('usuarios.urls')),
    path('eventos/', include('eventos.urls')),
    path('inscripciones/', include('inscripciones.urls')),
    path('asistencias/', include('asistencias.urls')),
    path('certificados/', include('certificados.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('pagos/', include('pagos.urls')),
    path('reportes/', include('reportes.urls')),
    
    # Dashboard (vista principal)
    path('dashboard/', include('dashboard.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
