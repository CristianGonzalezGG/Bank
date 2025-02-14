from django import forms
from django import forms
from .models import Client
import cv2
import os
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django import forms

class EmailForm(forms.Form):
    recipient_email = forms.EmailField(label="Correo del destinatario")
    subject = forms.CharField(label="Asunto", max_length=100)
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)

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
    imageSave = forms.ImageField(required=False)

    class Meta:
        model = Client
        fields = ['cardId', 'name', 'imageSave', 'email', 'phone_number', 'address']

from django import forms
from .models import Account

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_type']
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-select'}),
        }
