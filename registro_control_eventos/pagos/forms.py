"""
Formularios para la aplicación de Pagos
PRCE - Plataforma de Registro y Control de Eventos
"""

from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from .models import Pago, MetodoPago
from inscripciones.models import Inscripcion
from decimal import Decimal
import re


class PagoBaseForm(forms.ModelForm):
    """Formulario base para pagos"""
    
    class Meta:
        model = Pago
        fields = ['monto', 'notas']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            })
        }


class PagoEfectivoForm(PagoBaseForm):
    """Formulario para pagos en efectivo"""
    
    referencia = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de recibo (opcional)'
        }),
        help_text='Número de recibo o referencia interna'
    )
    
    class Meta(PagoBaseForm.Meta):
        fields = PagoBaseForm.Meta.fields + ['referencia']


class PagoTransferenciaForm(PagoBaseForm):
    """Formulario para pagos por transferencia bancaria"""
    
    banco = forms.ChoiceField(
        choices=[
            ('', 'Seleccione un banco'),
            ('BANCOLOMBIA', 'Bancolombia'),
            ('DAVIVIENDA', 'Davivienda'),
            ('BBVA', 'BBVA'),
            ('BOGOTA', 'Banco de Bogotá'),
            ('POPULAR', 'Banco Popular'),
            ('OCCIDENTE', 'Banco de Occidente'),
            ('CAJA_SOCIAL', 'Caja Social'),
            ('COLPATRIA', 'Colpatria'),
            ('OTRO', 'Otro')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    
    numero_comprobante = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 123456789'
        }),
        help_text='Número de comprobante de la transferencia',
        required=True
    )
    
    comprobante = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf'
        }),
        help_text='Subir imagen o PDF del comprobante (opcional)'
    )
    
    class Meta(PagoBaseForm.Meta):
        fields = PagoBaseForm.Meta.fields + ['banco', 'numero_comprobante', 'comprobante']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Almacenar datos adicionales en el campo referencia
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar información adicional en referencia
        banco = self.cleaned_data.get('banco')
        numero = self.cleaned_data.get('numero_comprobante')
        instance.referencia = f"TRANS-{banco}-{numero}"
        
        if commit:
            instance.save()
        return instance


class PagoTarjetaForm(PagoBaseForm):
    """Formulario para pagos con tarjeta (SIMULADO)"""
    
    numero_tarjeta = forms.CharField(
        max_length=19,
        validators=[
            RegexValidator(
                regex=r'^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$',
                message='Ingrese un número de tarjeta válido (16 dígitos)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'maxlength': '19',
            'autocomplete': 'cc-number'
        }),
        help_text='16 dígitos de la tarjeta (SIMULADO - acepta cualquier número)'
    )
    
    nombre_titular = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NOMBRE COMO APARECE EN LA TARJETA',
            'autocomplete': 'cc-name',
            'style': 'text-transform: uppercase'
        })
    )
    
    fecha_expiracion = forms.CharField(
        max_length=5,
        validators=[
            RegexValidator(
                regex=r'^\d{2}/\d{2}$',
                message='Formato: MM/AA'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/AA',
            'maxlength': '5',
            'autocomplete': 'cc-exp'
        })
    )
    
    cvv = forms.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r'^\d{3,4}$',
                message='CVV de 3 o 4 dígitos'
            )
        ],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '•••',
            'maxlength': '4',
            'autocomplete': 'cc-csc'
        })
    )
    
    tipo_tarjeta = forms.ChoiceField(
        choices=[
            ('CREDITO', 'Crédito'),
            ('DEBITO', 'Débito')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='CREDITO'
    )
    
    cuotas = forms.ChoiceField(
        choices=[
            ('1', 'Pago de Contado'),
            ('3', '3 cuotas'),
            ('6', '6 cuotas'),
            ('12', '12 cuotas'),
            ('24', '24 cuotas')
        ],
        initial='1',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualizar las cuotas según el tipo de tarjeta
        
    def clean_numero_tarjeta(self):
        """Validación adicional del número de tarjeta (SIMULADO)"""
        numero = self.cleaned_data.get('numero_tarjeta')
        # Eliminar espacios
        numero = numero.replace(' ', '')
        
        # En un sistema real, aquí iría el algoritmo de Luhn
        # Para la simulación, aceptamos cualquier número de 16 dígitos
        if len(numero) != 16 or not numero.isdigit():
            raise forms.ValidationError('Número de tarjeta inválido')
        
        return numero
    
    def clean_fecha_expiracion(self):
        """Validar que la tarjeta no esté vencida (SIMULADO)"""
        fecha = self.cleaned_data.get('fecha_expiracion')
        
        # Para la simulación, solo verificamos el formato
        # En un sistema real, verificaríamos contra la fecha actual
        if not re.match(r'^\d{2}/\d{2}$', fecha):
            raise forms.ValidationError('Formato inválido. Use MM/AA')
        
        return fecha
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar últimos 4 dígitos en la referencia
        numero = self.cleaned_data.get('numero_tarjeta').replace(' ', '')
        ultimos_digitos = numero[-4:]
        tipo = self.cleaned_data.get('tipo_tarjeta')
        instance.referencia = f"TARJETA-{tipo}-****{ultimos_digitos}"
        
        # Guardar detalles adicionales en datos_pasarela
        instance.datos_pasarela = {
            'tipo': tipo,
            'nombre_titular': self.cleaned_data.get('nombre_titular'),
            'expiracion': self.cleaned_data.get('fecha_expiracion'),
            'cuotas': self.cleaned_data.get('cuotas', '1')
        }
        
        if commit:
            instance.save()
        return instance





class ConfirmarPagoForm(forms.Form):
    """Formulario para confirmar/rechazar pagos manualmente"""
    
    ACCION_CHOICES = [
        ('CONFIRMAR', 'Confirmar Pago'),
        ('RECHAZAR', 'Rechazar Pago')
    ]
    
    accion = forms.ChoiceField(
        choices=ACCION_CHOICES,
        widget=forms.RadioSelect(),
        required=True
    )
    
    notas = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Motivo o notas adicionales'
        }),
        required=False
    )
