from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Client
from django.db import transaction

class Command(BaseCommand):
    help = 'Create users for existing clients'

    def handle(self, *args, **kwargs):
        clients_without_users = Client.objects.filter(user__isnull=True)
        
        with transaction.atomic():
            for client in clients_without_users:
                # Crear nombre de usuario base
                base_username = client.email.split('@')[0]
                username = base_username
                counter = 1
                
                # Asegurarse de que el username sea único
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Crear el usuario
                user = User.objects.create_user(
                    username=username,
                    email=client.email,
                    password='changeme123'  # Contraseña temporal
                )
                
                # Asignar el usuario al cliente
                client.user = user
                client.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created user {username} for client {client.name}'
                    )
                ) 