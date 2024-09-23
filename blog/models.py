from django.db import models

class Client(models.Model):
    
    class Status(models.TextChoices):
        OWE = 'O', 'OWE'
        NODEBT = 'ND', 'NODEBT'
         
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, 
                              choices=Status.choices,
                              default= Status.NODEBT)  # Estado del cliente por defecto en 'OWE' (deuda)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    # Método para obtener el número de cuenta enlazada
    def get_account_number(self):
        try:
            # Accedemos a la cuenta enlazada usando reverse lookup si existe
            return self.account.numberAccount
        except Account.DoesNotExist:
            return 'No Account'

class Account(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACT', 'Active'
        INACTIVE = 'INV', 'Inactive'
        REPORTED = 'RP', 'Reported'
        
    class AccountType(models.TextChoices):
        SAVINGS = 'SV', 'Savings'
        CHECKING = 'CK', 'Checking'
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='account')  # Relación uno a uno
    numberAccount = models.CharField(max_length=20, default='DEFAULT1')  
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, 
                              choices = Status.choices, 
                              default= Status.ACTIVE)
    account_type = models.CharField( max_length=2,  
                                    choices=AccountType.choices,
                                    default=AccountType.SAVINGS  )#como valor predetermidado ahorros)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.client.name}'s Account"
