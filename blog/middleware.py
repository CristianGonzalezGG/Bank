from django.shortcuts import redirect
from django.urls import reverse
from .models import UserTwoFactorSettings
from django.contrib import messages

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.email:
            # Lista de URLs excluidas de la verificación 2FA
            excluded_urls = [
                reverse('blog:verify_2fa'),
                reverse('blog:logout'),
                reverse('blog:login'),
                # Añadir otras URLs que deban estar excluidas
            ]
            
            if request.path not in excluded_urls:
                if not request.session.get('2fa_verified'):
                    messages.warning(request, 'Por favor complete la verificación de dos factores.')
                    return redirect('blog:verify_2fa')
        
        response = self.get_response(request)
        return response 