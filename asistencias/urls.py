"""
URLs para la aplicación de Asistencias
"""

from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    path('', views.lista_asistencias, name='lista'),
    path('control/', views.control_asistencias, name='control'),
    path('registrar/<int:inscripcion_id>/', views.registrar_asistencia, name='registrar'),
    path('qr/<uuid:codigo_qr>/', views.registrar_qr, name='registrar_qr'),
    path('evento/<int:evento_id>/', views.asistencias_evento, name='evento'),
]

