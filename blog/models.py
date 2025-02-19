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
from django.utils import timezone

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
                              default=Status.NODEBT)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:client_detail', args=[self.id])
    
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
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Cuenta de Ahorros'),
        ('CHECKING', 'Cuenta Corriente'),
        ('FIXED', 'Depósito a Plazo Fijo'),
        ('SALARY', 'Cuenta Sueldo')
    ]

    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    numberAccount = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Account {self.numberAccount} - {self.client.name}"

    def generate_account_number(self):
        while True:
            number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            if not Account.objects.filter(numberAccount=number).exists():
                return number

    def save(self, *args, **kwargs):
        if not self.numberAccount:
            self.numberAccount = self.generate_account_number()
        super().save(*args, **kwargs)

class Loan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    repayment_term = models.IntegerField(
        help_text="Número de meses para el reembolso",
        default=12
    )
    start_date = models.DateField(
        default=timezone.now,
        help_text="Fecha de inicio del préstamo"
    )
    status = models.CharField(
        max_length=20, 
        default='PENDING',
        choices=[
            ('PENDING', 'Pendiente'),
            ('ACTIVE', 'Activo'),
            ('PAID', 'Pagado'),
            ('DEFAULTED', 'Incumplido')
        ]
    )
    remaining_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    next_payment_date = models.DateField(
        null=True, 
        blank=True
    )
    monthly_payment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )

    def __str__(self):
        return f"Loan for {self.client.name} - ${self.amount}"

    def calculate_monthly_payment(self):
        r = self.interest_rate / 100 / 12  # Monthly interest rate
        n = self.repayment_term
        P = float(self.amount)
        
        # Monthly payment formula: P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        if r == 0:
            monthly_payment = P / n
        else:
            monthly_payment = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
        
        return round(monthly_payment, 2)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.remaining_balance = self.amount
            self.monthly_payment = self.calculate_monthly_payment()
            if not self.next_payment_date:
                self.next_payment_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def register_payment(self, payment_amount):
        if payment_amount <= self.remaining_balance:
            self.remaining_balance -= payment_amount
            if self.remaining_balance == 0:
                self.status = 'PAID'
            self.next_payment_date += timedelta(days=30)
            self.save()
            
            # Create payment record
            Payment.objects.create(
                loan=self,
                amount=payment_amount
            )
            return True
        return False

    def generate_certificate(self):
        if self.status != 'PAID':
            return None
        
        try:
            # Asegúrate de que el directorio media existe
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
            os.makedirs(cert_dir, exist_ok=True)

            # Generar nombre único para el archivo
            output_file = f'paz_y_salvo_{self.client.name}_{self.id}_{now().strftime("%Y%m%d%H%M%S")}.pdf'
            output_path = os.path.join(cert_dir, output_file)

            # Preparar el contexto
            context = {
                'loan': self,
                'client': self.client,
                'date': now().strftime('%d de %B de %Y'),
            }
            
            # Renderizar el template HTML
            html_content = render_to_string('loan/paz_y_salvo_template.html', context)
            
            # Configuración de pdfkit
            options = {
                'page-size': 'Letter',
                'encoding': 'UTF-8',
                'enable-local-file-access': True,
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'quiet': '',
            }

            try:
                # Intentar usar la configuración del settings
                config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_CMD)
                pdfkit.from_string(html_content, output_path, options=options, configuration=config)
            except Exception as pdf_error:
                print(f"Error con la configuración principal: {str(pdf_error)}")
                # Intentar sin configuración específica
                pdfkit.from_string(html_content, output_path, options=options)

            if not os.path.exists(output_path):
                raise Exception("El archivo PDF no se generó correctamente")

            # Enviar correo
            subject = 'Certificado de Paz y Salvo'
            message = f'''
            Estimado(a) {self.client.name},

            Adjunto encontrará su certificado de paz y salvo del préstamo #{self.id}.
            
            Gracias por confiar en nosotros.

            Atentamente,
            Banco El Dorado
            '''
            
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.client.email]
            )
            email.attach_file(output_path)
            email.send()
            
            return output_path
            
        except Exception as e:
            print(f"Error generando certificado: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de ${self.amount} para préstamo de {self.loan.client.name}"

class Appointment(models.Model):
    APPOINTMENT_TYPES = [
        ('LOAN', 'Solicitud de Préstamo'),
        ('SAVINGS', 'Apertura Cuenta de Ahorros'),
        ('CHECKING', 'Apertura Cuenta Corriente'),
        ('INVESTMENT', 'Asesoría de Inversiones'),
        ('CARDS', 'Solicitud de Tarjetas'),
        ('OTHER', 'Otros Servicios'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('COMPLETED', 'Cumplida'),
        ('CANCELLED', 'Cancelada'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    date = models.DateField()
    time = models.TimeField()
    branch = models.CharField(max_length=100)  # Sede
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Cita de {self.client.name} - {self.get_appointment_type_display()} - {self.date}"

class UserTwoFactorSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"2FA Settings for {self.user.username}"

class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_verified and self.expires_at > timezone.now()
