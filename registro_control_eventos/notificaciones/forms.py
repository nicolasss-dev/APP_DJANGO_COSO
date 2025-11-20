"""
Formularios para la aplicación de Notificaciones
PRCE - Plataforma de Registro y Control de Eventos
"""

from django import forms
from .models import Notificacion, PlantillaCorreo, TipoNotificacion, ConfiguracionRecordatorio
from usuarios.models import Usuario
from eventos.models import Evento


class EnviarNotificacionForm(forms.ModelForm):
    """Formulario para enviar notificaciones manuales"""
    
    destinatarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        help_text='Seleccione los destinatarios de la notificación'
    )
    
    plantilla = forms.ModelChoiceField(
        queryset=PlantillaCorreo.objects.filter(activa=True),
        empty_label='Seleccione una plantilla',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    
    asunto_personalizado = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dejar vacío para usar el asunto de la plantilla'
        }),
        help_text='Opcional: Personalizar el asunto del correo'
    )
    
    variables_contexto = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '{"variable1": "valor1", "variable2": "valor2"}'
        }),
        help_text='Variables adicionales en formato JSON (opcional)'
    )
    
    class Meta:
        model = Notificacion
        fields = ['asunto', 'cuerpo']
        widgets = {
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'cuerpo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'readonly': True
            })
        }


class PlantillaCorreoForm(forms.ModelForm):
    """Formulario para crear/editar plantillas de correo"""
    
    class Meta:
        model = PlantillaCorreo
        fields = ['tipo_notificacion', 'nombre', 'asunto', 'cuerpo_html', 
                  'cuerpo_texto', 'pie_pagina', 'variables_disponibles', 'activa']
        widgets = {
            'tipo_notificacion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo de la plantilla'
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Confirmación de Inscripción - {{evento.nombre}}'
            }),
            'cuerpo_html': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 10,
                'placeholder': '<p>Hola {{nombre}},</p><p>...</p>'
            }),
            'cuerpo_texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Versión en texto plano del correo'
            }),
            'pie_pagina': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Pie de página opcional'
            }),
            'variables_disponibles': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '{{nombre}}, {{evento.nombre}}, {{fecha}}'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class NotificacionRapidaForm(forms.Form):
    """Formulario para envío rápido de notificaciones"""
    
    destinatario_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        help_text='Email del destinatario'
    )
    
    asunto = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del correo'
        })
    )
    
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Mensaje a enviar...'
        })
    )


class ConfiguracionRecordatorioForm(forms.ModelForm):
    """Formulario para configurar recordatorios automáticos"""
    
    class Meta:
        model = ConfiguracionRecordatorio
        fields = ['evento', 'activo', 'horas_antes', 'mensaje_personalizado']
        widgets = {
            'evento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'horas_antes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 168,
                'step': 1
            }),
            'mensaje_personalizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mensaje adicional opcional para el recordatorio'
            })
        }
