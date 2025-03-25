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
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import User



from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import random
from decimal import Decimal

class Client(models.Model):
    cardId = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='Número de Identificación'
    )
    name = models.CharField(
        max_length=100, 
        verbose_name='Nombre Completo'
    )
    email = models.EmailField(
        verbose_name='Correo Electrónico'
    )
    phone_number = models.CharField(
        max_length=15, 
        verbose_name='Teléfono'
    )
    address = models.CharField(
        max_length=200, 
        verbose_name='Dirección'
    )
    imageSave = models.ImageField(
        upload_to='client_photos/', 
        verbose_name='Foto',
        null=True,  # Permitir valores nulos
        blank=True  # Permitir valores en blanco en formularios
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.cardId}"

    def get_absolute_url(self):
        return reverse('blog:client_detail', args=[self.id])

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS_NORMAL', 'Cuenta de Ahorros Normal'),
        ('SAVINGS_NOMINA', 'Cuenta Nómina'),
        ('SAVINGS_AMIGA', 'Cuenta Amiga'),
        ('CHECKING', 'Cuenta Corriente'),
    ]

    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='accounts'  # Asegúrate de que esto esté definido
    )
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)
    numberAccount = models.CharField(max_length=20, unique=True, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos específicos para cuenta corriente
    cvv = models.CharField(max_length=3, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    credit_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Límite de Crédito'
    )
    
    # Campos específicos para cuenta nómina
    company_nit = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        verbose_name='NIT de la Empresa'
    )
    company_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name='Nombre de la Empresa'
    )
    
    # Campo para clave virtual (solo cuentas de ahorro)
    virtual_key = models.CharField(
        max_length=6, 
        null=True, 
        blank=True,
        verbose_name='Clave Virtual'
    )

    def generate_account_number(self):
        prefix = {
            'SAVINGS_NORMAL': '10',
            'SAVINGS_NOMINA': '11',
            'SAVINGS_AMIGA': '12',
            'CHECKING': '20',
        }.get(self.account_type, '00')
        
        while True:
            number = f"{prefix}{''.join([str(random.randint(0, 9)) for _ in range(8)])}"
            if not Account.objects.filter(numberAccount=number).exists():
                return number

    def generate_cvv(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(3)])

    def generate_expiration_date(self):
        return datetime.now().date() + timedelta(days=1825)  # 5 años

    def generate_virtual_key(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def validate_account_limit(self, client):
        """Validar límites de cuenta por tipo"""
        if self.account_type.startswith('SAVINGS_'):
            savings_count = Account.objects.filter(
                client=client,
                account_type__in=['SAVINGS_NORMAL', 'SAVINGS_NOMINA', 'SAVINGS_AMIGA']
            ).count()
            if savings_count > 0:
                raise ValidationError('El cliente ya tiene una cuenta de ahorros activa.')
        
        elif self.account_type == 'CHECKING':
            checking_count = Account.objects.filter(
                client=client,
                account_type='CHECKING'
            ).count()
            if checking_count > 0:
                raise ValidationError('El cliente ya tiene una cuenta corriente activa.')

    def clean(self):
        super().clean()
        # La validación de límites se moverá a la vista

    def save(self, *args, **kwargs):
        if not self.pk:  # Solo para cuentas nuevas
            self.numberAccount = self.generate_account_number()
            
            if self.account_type.startswith('SAVINGS_'):
                self.virtual_key = self.generate_virtual_key()
            
            elif self.account_type == 'CHECKING':
                self.cvv = self.generate_cvv()
                self.expiration_date = self.generate_expiration_date()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_account_type_display()} - {self.numberAccount}"

    def get_account_type_display(self):
        """
        Método personalizado para manejar casos donde el tipo de cuenta pudiera no coincidir
        """
        try:
            return dict(self.ACCOUNT_TYPES)[self.account_type]
        except KeyError:
            # Si el tipo no existe en las opciones actuales, devolver un valor por defecto
            return "Tipo de cuenta no especificado"

    def is_savings_account(self):
        """
        Verifica si la cuenta es de cualquier tipo de ahorro
        """
        return self.account_type in ['SAVINGS_NORMAL', 'SAVINGS_NOMINA', 'SAVINGS_AMIGA']

    class Meta:
        ordering = ['-created_at']

class Loan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    repayment_term = models.IntegerField()
    start_date = models.DateField(default=timezone.now)
    next_payment_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendiente'),
            ('ACTIVE', 'Activo'),
            ('PAID', 'Pagado'),
            ('DEFAULTED', 'Incumplido')
        ],
        default='PENDING'
    )
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Campos de auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loans_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification = models.ForeignKey(
        'LoanVerification',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def calculate_monthly_payment(self):
        # Handle zero interest rate case separately
        if self.interest_rate == 0:
            # For zero interest, simple division of principal by term
            if self.repayment_term == 0:
                return Decimal('0')  # Handle zero term case
            return self.amount / Decimal(self.repayment_term)
        
        # Convert annual rate to monthly rate
        monthly_rate = self.interest_rate / Decimal('100') / Decimal('12')
        
        # Ensure term is not zero to avoid division by zero
        if self.repayment_term == 0:
            return Decimal('0')  # Return zero payment for zero term
        
        # Standard loan payment formula: P × r(1 + r)^n/((1 + r)^n - 1)
        # Where P = principal, r = monthly rate, n = number of payments
        n = Decimal(self.repayment_term)
        if monthly_rate == 0:
            return self.amount / n
        
        term_factor = (Decimal('1') + monthly_rate) ** n
        monthly_payment = self.amount * (monthly_rate * term_factor) / (term_factor - Decimal('1'))
        
        return monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def clean(self):
        if not self.pk:  # Solo para préstamos nuevos
            active_loans = Loan.objects.filter(
                client=self.client,
                status__in=['PENDING', 'ACTIVE']
            ).exists()
            
            if active_loans:
                raise ValidationError(
                    'El cliente tiene un préstamo activo pendiente de pago.'
                )

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:  # Only on creation
            self.remaining_balance = self.amount
            self.monthly_payment = self.calculate_monthly_payment()
            if not self.next_payment_date:
                self.next_payment_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def register_payment(self, payment_amount):
        """
        Registra un nuevo pago y actualiza el saldo del préstamo
        """
        # Convertir el monto del pago a Decimal
        payment_amount = Decimal(str(payment_amount))
        
        # Validar que el pago no exceda el saldo restante
        if payment_amount > self.remaining_balance:
            raise ValidationError(
                f'El monto del pago (${payment_amount}) no puede ser mayor al saldo restante (${self.remaining_balance})'
            )
        
        # Crear el registro de pago
        payment = Payment.objects.create(
            loan=self,
            amount=payment_amount,
            payment_date=timezone.now()
        )
        
        # Actualizar el saldo restante
        self.remaining_balance -= payment_amount
        
        # Si el saldo llega a cero, marcar el préstamo como pagado
        if self.remaining_balance <= Decimal('0'):
            self.status = 'PAID'
            self.remaining_balance = Decimal('0')
        else:
            # Actualizar la fecha del próximo pago
            self.next_payment_date = timezone.now() + timedelta(days=30)
        
        self.save()
        return payment

    def get_absolute_url(self):
        return reverse('blog:loan_detail', kwargs={'pk': self.id})

    def generate_certificate(self):
        if self.status != 'PAID':
            return None
        
        try:
            # Asegúrate de que el directorio media existe
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
            os.makedirs(cert_dir, exist_ok=True)

            # Generar nombre único para el archivo
            output_file = f'paz_y_salvo_{self.client.name}_{self.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}.pdf'
            output_path = os.path.join(cert_dir, output_file)

            # Preparar el contexto
            context = {
                'loan': self,
                'client': self.client,
                'date': timezone.now().strftime('%d de %B de %Y'),
            }
            
            # Renderizar el template HTML
            html_content = render_to_string('loan/certificate_template.html', context)
            
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

            # Generar PDF
            pdfkit.from_string(html_content, output_path, options=options)

            # Enviar correo
            subject = 'Certificado de Paz y Salvo - Banco El Dorado'
            message = f'''
            Estimado(a) {self.client.name},

            Adjunto encontrará su certificado de paz y salvo del préstamo #{self.id}.
            
            Gracias por su puntualidad en los pagos y por confiar en nosotros.

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
            return None

    def __str__(self):
        return f"Loan for {self.client} - ${self.amount}"

class Payment(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of ${self.amount} for loan {self.loan.id}"

    def save(self, *args, **kwargs):
        if not self.balance_after:
            self.balance_after = self.loan.remaining_balance - self.amount
        super().save(*args, **kwargs)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"2FA Code for {self.user.username}"

class LoanVerification(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    security_answers_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for {self.client} - {'Verified' if self.is_verified else 'Pending'}"

class SecurityQuestionTemplate(models.Model):
    question_text = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_text']

    def __str__(self):
        return self.question_text

class ClientSecurityQuestion(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='security_questions')
    question = models.ForeignKey(SecurityQuestionTemplate, on_delete=models.PROTECT)
    answer = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['client', 'question']

    def __str__(self):
        return f"Security Question for {self.client.name}"

    def save(self, *args, **kwargs):
        if self.answer:
            from django.contrib.auth.hashers import make_password
            self.answer = make_password(self.answer.lower())
        super().save(*args, **kwargs)

    def verify_answer(self, provided_answer):
        if not self.answer or not provided_answer:
            return False
        from django.contrib.auth.hashers import check_password
        return check_password(provided_answer.lower(), self.answer)

class Projection(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('REVIEWED', 'Revisado'),
        ('CONTACTED', 'Contactado')
    ]
    
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_interest = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_days = models.IntegerField()
    payment_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    advisor_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Projection for {self.client_name} - {self.initial_amount}"
