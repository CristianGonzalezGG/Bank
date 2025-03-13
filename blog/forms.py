from django import forms
from .models import Client, Account, Loan, Appointment
import cv2
import os
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django import forms
from django.utils import timezone



class EmailForm(forms.Form):
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el asunto del correo'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Escriba su mensaje aquí'
        })
    )

from django import forms
from .models import Loan

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'interest_rate', 'repayment_term']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'repayment_term': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'client': 'Cliente',
            'amount': 'Monto del préstamo',
            'interest_rate': 'Tasa de interés (%)',
            'repayment_term': 'Plazo (meses)',
        }
from django import forms
from .models import Client
from django.core.exceptions import ValidationError

class ClientForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control input-hover',
            'placeholder': 'Ingrese el nombre completo'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'max_length': 'Máximo 100 caracteres permitidos.'
        }
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control input-hover',
            'placeholder': 'Correo electrónico'
        }),
        error_messages={
            'invalid': 'Ingrese un correo electrónico válido.',
            'required': 'El correo es obligatorio.'
        }
    )

    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control input-hover',
            'placeholder': 'Número de teléfono'
        }),
        error_messages={
            'required': 'El número de teléfono es obligatorio.',
            'max_length': 'Máximo 15 caracteres permitidos.'
        }
    )

    address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control input-hover',
            'placeholder': 'Dirección'
        }),
        error_messages={
            'required': 'La dirección es obligatoria.',
            'max_length': 'Máximo 200 caracteres permitidos.'
        }
    )

    imageSave = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control input-hover',
            'accept': 'image/*'
        }),
        error_messages={
            'required': 'Debe subir una imagen del cliente.'
        }
    )

    class Meta:
        model = Client
        fields = ['name', 'email', 'phone_number', 'address', 'imageSave']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise ValidationError("El número de teléfono solo debe contener dígitos.")
        if len(phone) < 7 or len(phone) > 15:
            raise ValidationError("El número debe tener entre 7 y 15 dígitos.")
        return phone

    def clean_imageSave(self):
        image = self.cleaned_data.get('imageSave')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("La imagen no debe superar los 5MB.")
            if not image.content_type.startswith('image'):
                raise ValidationError("El archivo debe ser una imagen válida.")
        return image



from django import forms
from .models import Account

class AccountForm(forms.ModelForm):
    initial_deposit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label="Depósito Inicial",
        help_text="Monto mínimo para apertura: $0"
    )

    class Meta:
        model = Account
        fields = ['account_type']
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_type'].widget.attrs.update({
            'class': 'form-control',
            'required': 'required'
        })

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_type', 'date', 'time', 'branch', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'},
                choices=[
                    ('SEDE_NORTE', 'Sede Norte'),
                    ('SEDE_SUR', 'Sede Sur'),
                    ('SEDE_CENTRO', 'Sede Centro'),
                    ('SEDE_OESTE', 'Sede Oeste'),
                ]),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            })
        }

class PQRForm(forms.Form):
    TIPOS_PQR = [
        ('PETICION', 'Petición'),
        ('QUEJA', 'Queja'),
        ('RECLAMO', 'Reclamo'),
    ]
    
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre completo'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    documento = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de identificación'})
    )
    telefono = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'})
    )
    tipo = forms.ChoiceField(
        choices=TIPOS_PQR,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    asunto = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto de su solicitud'})
    )
    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describa detalladamente su solicitud'})
    )
    autorizacion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

