"""
Formularios para la aplicación de Inscripciones
HU-03: Registro de Asistentes
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import Inscripcion


class InscripcionPublicaForm(forms.ModelForm):
    """
    Formulario público para inscripción a eventos (HU-03)
    Accesible sin login - permite registro de usuarios externos
    """
    
    class Meta:
        model = Inscripcion
        fields = ['nombre', 'apellido', 'documento', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre',
                'required': True,
                'maxlength': 100
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su apellido',
                'required': True,
                'maxlength': 100
            }),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento',
                'required': True,
                'maxlength': 20
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'required': True,
                'type': 'email'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'required': True,
                'maxlength': 15
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'documento': 'Documento de Identidad',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
        }
    
    def __init__(self, *args, evento=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.evento = evento
        self.usuario = usuario
        
        # Autocompletar datos si el usuario está autenticado
        if usuario and usuario.is_authenticated:
            if not self.initial:
                self.initial = {}
            
            # Solo autocompletar si los campos están vacíos
            if not self.initial.get('nombre') and usuario.first_name:
                self.initial['nombre'] = usuario.first_name
            if not self.initial.get('apellido') and usuario.last_name:
                self.initial['apellido'] = usuario.last_name
            if not self.initial.get('correo') and usuario.email:
                self.initial['correo'] = usuario.email
            if not self.initial.get('telefono') and usuario.telefono:
                self.initial['telefono'] = usuario.telefono
            if not self.initial.get('documento') and usuario.documento:
                self.initial['documento'] = usuario.documento
    
    def clean_correo(self):
        """Validar formato de correo electrónico"""
        correo = self.cleaned_data.get('correo')
        
        # Validar formato
        validator = EmailValidator()
        try:
            validator(correo)
        except ValidationError:
            raise ValidationError('Por favor ingrese un correo electrónico válido')
        
        # Validar que no esté inscrito previamente (HU-03, Criterio 3)
        if self.evento:
            if Inscripcion.objects.filter(
                evento=self.evento,
                correo=correo
            ).exists():
                raise ValidationError('Ya se encuentra inscrito a este evento')
        
        return correo
    
    def clean_documento(self):
        """Validar documento"""
        documento = self.cleaned_data.get('documento')
        
        if not documento:
            return documento
        
        # Validar que solo contenga números
        if not documento.isdigit():
            raise ValidationError('El documento debe contener solo números')
        
        # Validar longitud mínima
        if len(documento) < 6:
            raise ValidationError('El documento debe tener al menos 6 dígitos')
        
        # Validar documento único por evento
        if self.evento:
            if Inscripcion.objects.filter(
                evento=self.evento,
                documento=documento
            ).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                raise ValidationError('Ya existe una inscripción con este documento para este evento')
        
        return documento
    
    def clean_telefono(self):
        """Validar formato de teléfono"""
        telefono = self.cleaned_data.get('telefono')
        
        # Remover espacios y guiones
        telefono = telefono.replace(' ', '').replace('-', '')
        
        # Validar que solo contenga números
        if not telefono.isdigit():
            raise ValidationError('El teléfono debe contener solo números')
        
        # Validar longitud
        if len(telefono) < 7 or len(telefono) > 15:
            raise ValidationError('El teléfono debe tener entre 7 y 15 dígitos')
        
        return telefono
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        
        # Verificar que todos los campos estén completos (HU-03, Criterio 2)
        campos_requeridos = ['nombre', 'apellido', 'documento', 'correo', 'telefono']
        for campo in campos_requeridos:
            if not cleaned_data.get(campo):
                raise ValidationError(
                    'Por favor complete todos los campos requeridos'
                )
        
        return cleaned_data

