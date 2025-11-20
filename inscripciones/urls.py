"""
URLs para la aplicación de Inscripciones
"""

from django.urls import path
from . import views

app_name = 'inscripciones'

urlpatterns = [
    path('', views.lista_inscripciones, name='lista'),
    path('registro-publico/', views.registro_publico, name='registro_publico'),
    path('registro-publico/<int:evento_id>/', views.registro_publico_evento, name='registro_publico_evento'),
    path('confirmacion/<int:pk>/', views.confirmacion_inscripcion, name='confirmacion_inscripcion'),
    path('registro-masivo/', views.registro_masivo, name='registro_masivo'),
    path('<int:pk>/', views.detalle_inscripcion, name='detalle'),
    path('<int:pk>/confirmar/', views.confirmar_inscripcion, name='confirmar'),
    path('<int:pk>/cancelar/', views.cancelar_inscripcion, name='cancelar'),
]

