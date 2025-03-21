from django import forms
from .models import Client, Account, Loan, Appointment
import cv2
import os
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django import forms
from django.utils import timezone
from django import forms
from decimal import Decimal

from django import forms

class IDVerificationForm(forms.Form):
    # Campo para subir la imagen del ID
    id_image = forms.ImageField(
        label="Subir imagen de ID",
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    # Campo para seleccionar el tipo de documento
    DOCUMENT_TYPES = [
        ('ID', 'Documento de Identidad'),
        ('PASSPORT', 'Pasaporte'),
        ('DRIVER_LICENSE', 'Licencia de Conducir'),
    ]
    document_type = forms.ChoiceField(
        label="Tipo de Documento",
        choices=DOCUMENT_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para seleccionar el país
    COUNTRIES = [
        ('CO', 'Colombia'),
        ('US', 'Estados Unidos'),
        ('MX', 'México'),
        # Agrega más países según sea necesario
    ]
    country = forms.ChoiceField(
        label="País",
        choices=COUNTRIES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para ingresar el número de documento
    document_number = forms.CharField(
        label="Número de Documento",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

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
from django import forms
from .models import Account
from django.core.validators import MinValueValidator

from django import forms
from .models import Account
from django.core.validators import MinValueValidator

class AccountForm(forms.ModelForm):
    initial_deposit = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        decimal_places=2,
        label='Depósito Inicial',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    company_nit = forms.CharField(
        required=False,
        max_length=20,
        label='NIT de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    company_name = forms.CharField(
        required=False,
        max_length=100,
        label='Nombre de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    credit_limit = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        decimal_places=2,
        label='Cupo de Crédito',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Account
        fields = ['account_type']
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')

        if account_type:
            if account_type.startswith('SAVINGS_'):
                initial_deposit = cleaned_data.get('initial_deposit')
                if initial_deposit is None or initial_deposit < Decimal('50000'):
                    raise forms.ValidationError('Las cuentas de ahorro requieren un depósito inicial mínimo de $50,000')

                if account_type == 'SAVINGS_NOMINA':
                    if not cleaned_data.get('company_nit'):
                        raise forms.ValidationError('El NIT de la empresa es requerido para cuentas nómina')
                    if not cleaned_data.get('company_name'):
                        raise forms.ValidationError('El nombre de la empresa es requerido para cuentas nómina')

            elif account_type == 'CHECKING':
                credit_limit = cleaned_data.get('credit_limit')
                if credit_limit is None or credit_limit <= 0:
                    raise forms.ValidationError('Debe especificar un cupo de crédito válido para cuenta corriente')

        return cleaned_data

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

