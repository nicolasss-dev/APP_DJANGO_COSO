"""
Formularios para la aplicación de Usuarios
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Usuario
import re


class LoginForm(forms.Form):
    """Formulario de inicio de sesión (HU-04)"""
    username = forms.CharField(
        label='Usuario o Correo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o correo electrónico',
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Recordarme',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class RegistroPublicoForm(forms.ModelForm):
    """Formulario público de registro de usuarios (HU-04)"""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        help_text='Mínimo 8 caracteres, incluyendo mayúsculas, minúsculas y números'
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita la contraseña',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'documento', 'telefono', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'required': True,
                'type': 'email'
            }),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'required': True
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario',
                'required': True
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'documento': 'Documento de Identidad',
            'telefono': 'Teléfono',
            'username': 'Nombre de Usuario',
        }
    
    def clean_password1(self):
        """Validar contraseña segura (HU-33)"""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe contener al menos una mayúscula')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('La contraseña debe contener al menos una minúscula')
        
        if not re.search(r'\d', password):
            raise ValidationError('La contraseña debe contener al menos un número')
        
        # Contraseñas comunes no permitidas
        contraseñas_comunes = ['password', '12345678', 'password123', 'admin123', '123456789']
        if password.lower() in contraseñas_comunes:
            raise ValidationError('Esta contraseña es muy común. Por favor elija otra.')
        
        return password
    
    def clean_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden')
        
        return password2
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado')
        return email
    
    def clean_documento(self):
        """Validar que el documento sea único"""
        documento = self.cleaned_data.get('documento')
        if not documento.isdigit():
            raise ValidationError('El documento debe contener solo números')
        if Usuario.objects.filter(documento=documento).exists():
            raise ValidationError('Este documento ya está registrado')
        return documento
    
    def clean_username(self):
        """Validar que el username sea único"""
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso')
        return username
    
    def save(self, commit=True):
        """Guardar usuario con contraseña"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.rol = 'ASISTENTE'  # Todos los registros públicos son asistentes
        user.activo = True
        if commit:
            user.save()
        return user


class UsuarioForm(UserCreationForm):
    """Formulario para crear/editar usuario (HU-11)"""
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'documento', 'telefono', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        """Validar que el email sea único (HU-11)"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError('Este correo ya está registrado')
        return email
    
    def clean_documento(self):
        """Validar que el documento sea único (HU-11)"""
        documento = self.cleaned_data.get('documento')
        if Usuario.objects.filter(documento=documento).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError('Este documento ya está registrado')
        return documento


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario (HU-13)"""
    password_actual = forms.CharField(
        required=False,
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    nueva_password = forms.CharField(
        required=False,
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        }),
        help_text='Deje vacío si no desea cambiar la contraseña'
    )
    confirmar_password = forms.CharField(
        required=False,
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Validar que el email sea único excepto el propio (HU-13)"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este correo ya está registrado')
        return email
    
    def clean(self):
        """Validar cambio de contraseña"""
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        # Si se intenta cambiar contraseña
        if nueva_password or confirmar_password or password_actual:
            if not password_actual:
                raise ValidationError({
                    'password_actual': 'Debe ingresar su contraseña actual para cambiarla'
                })
            
            # Verificar contraseña actual
            if not self.instance.check_password(password_actual):
                raise ValidationError({
                    'password_actual': 'La contraseña actual es incorrecta'
                })
            
            # Validar nueva contraseña
            if not nueva_password:
                raise ValidationError({
                    'nueva_password': 'Debe ingresar una nueva contraseña'
                })
            
            if len(nueva_password) < 8:
                raise ValidationError({
                    'nueva_password': 'La contraseña debe tener al menos 8 caracteres'
                })
            
            if nueva_password != confirmar_password:
                raise ValidationError({
                    'confirmar_password': 'Las contraseñas no coinciden'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar perfil y cambiar contraseña si se proporcionó"""
        user = super().save(commit=False)
        
        nueva_password = self.cleaned_data.get('nueva_password')
        if nueva_password:
            user.set_password(nueva_password)
        
        if commit:
            user.save()
        
        return user


class RecuperarPasswordForm(forms.Form):
    """Formulario para recuperar contraseña (HU-33)"""
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True,
            'autocomplete': 'email'
        })
    )
