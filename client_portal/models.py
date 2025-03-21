from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ProjectionRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('IN_REVIEW', 'En Revisión'),
        ('RESPONDED', 'Respondida'),
        ('CLOSED', 'Cerrada')
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projection_requests')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handled_projections', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Datos de la proyección
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_days = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    payment_type = models.CharField(max_length=20)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_interest = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Campos adicionales
    client_notes = models.TextField(blank=True)
    advisor_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Proyección {self.id} - Cliente: {self.client.username}"

class ProjectionResponse(models.Model):
    projection = models.ForeignKey(ProjectionRequest, on_delete=models.CASCADE, related_name='responses')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Respuesta a proyección {self.projection.id}"

class SimpleProjection(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    term_days = models.IntegerField(default=360)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payment_type = models.CharField(
        max_length=20, 
        choices=[
            ('maturity', 'Al vencimiento'),
            ('monthly', 'Mensual')
        ],
        default='maturity'
    )
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        default='PENDING',
        choices=[
            ('PENDING', 'Pendiente'),
            ('REVIEWED', 'Revisado'),
            ('CONTACTED', 'Contactado')
        ]
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Proyección de {self.name} - ${self.initial_amount:,.2f}"
