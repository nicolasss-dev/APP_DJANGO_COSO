"""
URLs para la aplicación de Usuarios
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_publico, name='registro_publico'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Gestión de usuarios (Administradores)
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/activar-desactivar/', views.activar_desactivar_usuario, name='activar_desactivar'),
]

