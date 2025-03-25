from django.shortcuts import redirect
from django.urls import reverse
from .models import UserTwoFactorSettings
from django.contrib import messages

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # URLs que no requieren 2FA
            exempt_urls = [
                reverse('blog:verify_2fa'),
                reverse('blog:logout'),
                '/static/',
                '/media/',
            ]
            
            # Verificar si la URL actual está exenta
            is_exempt = any(request.path.startswith(url) for url in exempt_urls)
            
            if not is_exempt:
                try:
                    two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
                    if two_factor_settings.is_enabled and not request.session.get('2fa_verified', False):
                        # Guardar la URL original para redireccionar después
                        request.session['next_url'] = request.path
                        return redirect('blog:verify_2fa')
                except UserTwoFactorSettings.DoesNotExist:
                    # Si no existe la configuración 2FA, crearla
                    UserTwoFactorSettings.objects.create(user=request.user, is_enabled=True)
                    return redirect('blog:verify_2fa')

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        # Rutas exentas de verificación 2FA
        exempt_urls = [
            reverse('blog:verify_2fa'),
            reverse('blog:enable_2fa'),
            reverse('blog:disable_2fa'),
            reverse('blog:logout'),
        ]

        if request.path in exempt_urls:
            return None

        try:
            # Verificar si el usuario tiene 2FA habilitado
            two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
            
            if two_factor_settings.is_enabled:
                # Verificar si la sesión está verificada
                if not request.session.get('2fa_verified'):
                    request.session['next_url'] = request.path
                    return redirect('blog:verify_2fa')
        except UserTwoFactorSettings.DoesNotExist:
            pass

        return None

# URLs públicas que no requieren autenticación
PUBLIC_URLS = [
    r'^inversiones/$',
    r'^proyecciones/$',
    r'^tramites/$',
    # ... otras URLs públicas ...
] 