from django.db import models
from django.urls import reverse

class Client(models.Model):
    
    class Status(models.TextChoices):
        OWE = 'O', 'OWE'
        NODEBT = 'ND', 'NODEBT'
         
    name = models.CharField(max_length=100)
    image = models.URLField(blank=True)
    imageSave = models.ImageField(blank=True)
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
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='account')
    numberAccount = models.CharField(max_length=20, default='DEFAULT1')  
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, 
                              choices=Status.choices, 
                              default=Status.ACTIVE)
    account_type = models.CharField(max_length=2,  
                                     choices=AccountType.choices,
                                     default=AccountType.SAVINGS)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.client.name}'s Account"

    def get_absolute_url(self):
        return reverse('blog:client_detail', args=[self.id])
    
