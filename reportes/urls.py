"""
URLs para reportes
"""

from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('asistencia/<int:evento_id>/', views.reporte_asistencia, name='asistencia'),
    path('asistencia/<int:evento_id>/pdf/', views.exportar_reporte_pdf, name='exportar_pdf'),
    path('asistencia/<int:evento_id>/excel/', views.exportar_reporte_excel, name='exportar_excel'),
]

