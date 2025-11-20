"""
Formularios para la aplicación de Eventos
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Evento, TipoEvento


class EventoForm(forms.ModelForm):
    """Formulario para crear/editar eventos (HU-01, HU-02)"""
    
    class Meta:
        model = Evento
        fields = [
            'nombre', 'descripcion', 'tipo_evento',
            'fecha_inicio', 'fecha_fin',
            'lugar', 'direccion',
            'cupo_maximo', 'costo',
            'imagen_banner',
            'numero_sesiones', 'porcentaje_asistencia_minimo',
            'genera_certificado', 'requiere_aprobacion',
            'estado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Jornada de Bienvenida 2025'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Breve descripción del evento, actividades previstas, etc.'
            }),
            'tipo_evento': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Auditorio Principal'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'cupo_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'imagen_banner': forms.FileInput(attrs={'class': 'form-control'}),
            'numero_sesiones': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'porcentaje_asistencia_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'value': 80
            }),
            'genera_certificado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requiere_aprobacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Evento',
            'descripcion': 'Descripción',
            'tipo_evento': 'Tipo de Evento',
            'fecha_inicio': 'Fecha y Hora de Inicio',
            'fecha_fin': 'Fecha y Hora de Fin',
            'lugar': 'Lugar',
            'direccion': 'Dirección',
            'cupo_maximo': 'Cupo Máximo',
            'costo': 'Costo de Inscripción',
            'imagen_banner': 'Banner del Evento',
            'numero_sesiones': 'Número de Sesiones',
            'porcentaje_asistencia_minimo': 'Asistencia Mínima para Certificado (%)',
            'genera_certificado': 'Genera certificado',
            'requiere_aprobacion': 'Requiere aprobación',
            'estado': 'Estado',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No mostrar campo estado en creación
        if not self.instance.pk:
            self.fields.pop('estado')
    
    def clean(self):
        """Validaciones personalizadas (HU-01)"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        # Validar que fecha_fin sea posterior a fecha_inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        return cleaned_data
    
    def clean_nombre(self):
        """Validar longitud del nombre (HU-01: máximo 200 caracteres)"""
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) > 200:
            raise ValidationError('El nombre no puede exceder 200 caracteres')
        return nombre
    
    def clean_cupo_maximo(self):
        """Validar cupo máximo (HU-01: número entero positivo)"""
        cupo_maximo = self.cleaned_data.get('cupo_maximo')
        if cupo_maximo < 1:
            raise ValidationError('El cupo máximo debe ser al menos 1')
        return cupo_maximo
    
    def clean_costo(self):
        """Validar costo (HU-01: número decimal con 2 decimales)"""
        costo = self.cleaned_data.get('costo')
        if costo < 0:
            raise ValidationError('El costo no puede ser negativo')
        return round(costo, 2)
