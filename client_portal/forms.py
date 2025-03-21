from django import forms
from .models import SimpleProjection
from django.utils.encoding import force_str

class ProjectionForm(forms.ModelForm):
    def clean_name(self):
        return force_str(self.cleaned_data['name'])

    def clean_email(self):
        return force_str(self.cleaned_data['email'])

    class Meta:
        model = SimpleProjection
        fields = ['name', 'email', 'initial_amount']
        labels = {
            'name': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'initial_amount': 'Monto de Inversión'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'accept-charset': 'utf-8'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'accept-charset': 'utf-8'
            }),
            'initial_amount': forms.NumberInput(attrs={'class': 'form-control'})
        }
