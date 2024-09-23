from django.contrib import admin
from .models import Client, Account

# Personalización del administrador para el modelo Client

# Registra los modelos en el admin
admin.site.register(Client)
admin.site.register(Account)
