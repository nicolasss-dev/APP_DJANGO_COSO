"""
URLs para la aplicación de Pagos
"""

from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.lista_pagos, name='lista'),
    path('registrar/<int:inscripcion_id>/', views.registrar_pago, name='registrar'),
    path('<int:pk>/confirmar/', views.confirmar_pago, name='confirmar'),
    path('reporte/<int:evento_id>/', views.reporte_financiero, name='reporte'),
]

