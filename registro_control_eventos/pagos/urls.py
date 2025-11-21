"""
URLs para la aplicación de Pagos
"""

from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.lista_pagos, name='lista'),
    
    # Selección y procesamiento de pagos
    path('pagar/<int:inscripcion_id>/', views.seleccionar_metodo_pago, name='seleccionar_metodo'),
    path('pagar/<int:inscripcion_id>/efectivo/', views.procesar_pago_efectivo, name='pagar_efectivo'),
    path('pagar/<int:inscripcion_id>/transferencia/', views.procesar_pago_transferencia, name='pagar_transferencia'),
    path('pagar/<int:inscripcion_id>/tarjeta/', views.procesar_pago_tarjeta, name='pagar_tarjeta'),

    
    # Gestión de pagos
    path('<int:pago_id>/', views.detalle_pago, name='detalle'),
    path('<int:pago_id>/confirmacion/', views.confirmacion_pago, name='confirmacion'),
    path('<int:pago_id>/confirmar-manual/', views.confirmar_pago_manual, name='confirmar_manual'),
    
    # Reportes
    path('reporte/<int:evento_id>/', views.reporte_financiero, name='reporte'),
]


