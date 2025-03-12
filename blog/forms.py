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

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['cardId', 'name', 'email', 'phone_number', 'address', 'imageSave']
        widgets = {
            'cardId': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de identificación'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+XX XXX XXX XXXX'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'imageSave': forms.HiddenInput()
        }

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

