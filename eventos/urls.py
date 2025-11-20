"""
URLs para la aplicación de Eventos
"""

from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    path('', views.lista_eventos, name='lista'),
    path('crear/', views.crear_evento, name='crear'),
    path('<int:pk>/', views.detalle_evento, name='detalle'),
    path('<int:pk>/editar/', views.editar_evento, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_evento, name='eliminar'),
    path('<int:pk>/duplicar/', views.duplicar_evento, name='duplicar'),
    path('<int:pk>/publicar/', views.publicar_evento, name='publicar'),
    path('<int:pk>/cancelar/', views.cancelar_evento, name='cancelar'),
]

