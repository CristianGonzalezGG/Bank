from django import forms

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