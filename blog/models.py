from django.core.mail import EmailMessage
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from datetime import datetime, timedelta
import os
import pdfkit
import random
from django.conf import settings

class Client(models.Model):
    
    class Status(models.TextChoices):
        OWE = 'O', 'OWE'
        NODEBT = 'ND', 'NODEBT'
    cardId = models.CharField(max_length= 10, null= True, blank = True)       
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='client_photos/', blank=True, null=True)
    imageSave = models.ImageField(upload_to='client_photos/', blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, 
                              choices=Status.choices,
                              default=Status.NODEBT)  # Estado del cliente por defecto en 'OWE' (deuda)
    
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:client_detail', args=[self.id])
    
    # Método para obtener el número de cuenta enlazada
    def get_account_number(self):
        try:
            return self.account.numberAccount
        except Account.DoesNotExist:
            return 'No Account'
    def get_type(self):
        try:
            return self.account.account_type
        except Account.DoesNotExist:
            return 'NOT TYPE'

class Account(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACT', 'Active'
        INACTIVE = 'INV', 'Inactive'
        REPORTED = 'RP', 'Reported'

    class AccountType(models.TextChoices):
        SAVINGS = 'SV', 'Savings'
        CHECKING = 'CK', 'Checking'

    client = models.OneToOneField("Client", on_delete=models.CASCADE, related_name='account')
    numberAccount = models.CharField(max_length=20, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.ACTIVE)
    account_type = models.CharField(max_length=2, choices=AccountType.choices, default=AccountType.SAVINGS)

    # Tarjeta de Débito
    debit_card_number = models.CharField(max_length=16, unique=True, null=True, blank=True, editable=False)
    debit_expiration_date = models.DateField(null=True, blank=True, editable=False)
    debit_cvv = models.CharField(max_length=3, null=True, blank=True, editable=False)

    # Tarjeta de Crédito
    credit_card_number = models.CharField(max_length=16, unique=True, null=True, blank=True, editable=False)
    credit_expiration_date = models.DateField(null=True, blank=True, editable=False)
    credit_cvv = models.CharField(max_length=3, null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.get_account_type_display()} Account"

    def get_absolute_url(self):
        return reverse('blog:client_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.numberAccount:
            self.numberAccount = self.generate_account_number()

        if not self.debit_card_number:
            self.debit_card_number = self.generate_unique_card_number()
            self.debit_expiration_date = self.generate_expiration_date()
            self.debit_cvv = self.generate_cvv()

        if not self.credit_card_number:
            self.credit_card_number = self.generate_unique_card_number()
            self.credit_expiration_date = self.generate_expiration_date()
            self.credit_cvv = self.generate_cvv()

        super().save(*args, **kwargs)

    @staticmethod
    def generate_account_number():
        return "AC" + str(random.randint(1000000000, 9999999999))

    @staticmethod
    def generate_cvv():
        return str(random.randint(100, 999))

    @staticmethod
    def generate_expiration_date():
        return datetime.now().date() + timedelta(days=365 * 5)  # 5 años de validez

    @staticmethod
    def generate_unique_card_number():
        """ Genera un número de tarjeta único en la base de datos. """
        while True:
            card_number = "".join(str(random.randint(0, 9)) for _ in range(16))
            if not Account.objects.filter(credit_card_number=card_number).exists() and \
               not Account.objects.filter(debit_card_number=card_number).exists():
                return card_number

class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('ONGOING', 'En Curso'),
        ('PAID', 'Pagado')
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    repayment_term = models.IntegerField(help_text="Número de meses para el reembolso")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_balance = self.amount
        
        if self.remaining_balance <= 0:
            self.remaining_balance = 0
            self.status = 'PAID'
        elif self.remaining_balance < self.amount:
            self.status = 'ONGOING'
        
        super().save(*args, **kwargs)

    def register_payment(self, amount):
        if amount > 0:
            self.remaining_balance = max(0, self.remaining_balance - amount)
            Payment.objects.create(loan=self, amount=amount)
            self.save()

    def generate_certificate(self):
        """Genera un certificado de paz y salvo"""
        if self.status == 'PAID':
            try:
                context = {
                    'client': self.client,
                    'loan': self,
                    'date': now().date()
                }
                
                # Asegúrate de que el directorio existe
                certificate_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
                os.makedirs(certificate_dir, exist_ok=True)
                
                pdf_path = os.path.join(certificate_dir, f'certificate_{self.id}.pdf')
                
                # Renderiza el template HTML
                html_string = render_to_string('loan/certificate_template.html', context)
                
                # Configuración de pdfkit
                options = {
                    'page-size': 'Letter',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None
                }
                
                # Genera el PDF
                config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # Ajusta esta ruta según tu sistema
                pdfkit.from_string(html_string, pdf_path, options=options, configuration=config)
                
                # Envía el certificado por correo
                self.send_certificate_email(pdf_path)
                
                return pdf_path
            except Exception as e:
                print(f"Error generando el certificado: {str(e)}")
                return None
        return None

    def send_certificate_email(self, pdf_path):
        """Envía el certificado por correo electrónico"""
        subject = 'Certificado de Paz y Salvo - Banco El Dorado'
        message = f'Estimado {self.client.name},\n\nAdjunto encontrará su certificado de paz y salvo.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.client.email]
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list
        )
        
        email.attach_file(pdf_path)
        email.send()

    def get_absolute_url(self):
        return reverse('blog:loan_detail', args=[str(self.id)])

    def __str__(self):
        return f"Préstamo de {self.client.name} - ${self.amount}"

    def get_payment_history(self):
        """Obtiene el historial de pagos ordenado por fecha"""
        return self.payments.all().order_by('-payment_date')

# Movemos la clase Payment después de Loan
class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de ${self.amount} para préstamo de {self.loan.client.name}"
