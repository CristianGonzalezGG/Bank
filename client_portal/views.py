from django.urls import path
from . import views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ProjectionRequest, ProjectionResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import json
from decimal import Decimal
from django.utils.html import strip_tags
from django.utils.encoding import force_str

app_name = 'client_portal'  # Añade esta línea

urlpatterns = [

]

@login_required
def save_projection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            projection = ProjectionRequest.objects.create(
                client=request.user,
                initial_amount=Decimal(data.get('initial_amount')),
                term_days=int(data.get('term_days')),
                interest_rate=Decimal(data.get('interest_rate')),
                payment_type=data.get('payment_type'),
                final_amount=Decimal(data.get('final_amount')) / Decimal('100'),  # Convertir de centavos
                net_interest=Decimal(data.get('net_interest')) / Decimal('100'),  # Convertir de centavos
                client_notes=data.get('notes', ''),
                status='PENDING'
            )
            
            # Enviar notificación por correo a los asesores
            subject = 'Nueva Proyección CDT Pendiente'
            message = f'''
            Se ha recibido una nueva solicitud de proyección CDT.
            
            Cliente: {data.get('client_name')}
            Email: {data.get('client_email')}
            Monto: ${data.get('initial_amount')}
            Plazo: {data.get('term_days')} días
            
            Por favor revise la solicitud en el panel de gestión.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADVISOR_EMAIL],  # Asegúrate de configurar esto en settings.py
                fail_silently=True,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Proyección guardada exitosamente',
                'projection_id': projection.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def advisor_projections(request):
    projections = ProjectionRequest.objects.all().order_by('-created_at')
    return render(request, 'client_portal/advisor/projections_list.html', {
        'projections': projections
    })

@login_required
def projection_detail(request, projection_id):
    projection = get_object_or_404(ProjectionRequest, id=projection_id)
    if request.method == 'POST':
        try:
            # Forzar codificación UTF-8 para los datos del formulario
            subject = force_str(request.POST.get('subject', ''))
            message = force_str(request.POST.get('message', ''))
            
            # Crear la respuesta
            response = ProjectionResponse.objects.create(
                projection=projection,
                advisor=request.user,
                subject=subject,
                message=message
            )
            
            # Preparar el contexto para el email asegurando codificación UTF-8
            context = {
                'client_name': force_str(projection.client.get_full_name() or projection.client.username),
                'advisor_name': force_str(request.user.get_full_name() or request.user.username),
                'projection': projection,
                'response': response,
                'bank_info': {
                    'name': 'Banco El Dorado',
                    'phone': '+57 1234567890',
                    'email': 'contacto@bancoeldorado.com',
                    'website': 'www.bancoeldorado.com'
                }
            }
            
            # Renderizar el template HTML con codificación UTF-8
            html_content = render_to_string(
                'client_portal/emails/projection_response.html',
                context
            ).encode('utf-8').decode('utf-8')
            
            # Crear versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear y enviar el email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[projection.client.email],
                alternatives=[(html_content, 'text/html')],
                encoding='utf-8'
            )
            
            email.send(fail_silently=False)
            
            # Actualizar estado
            response.email_sent = True
            response.email_sent_at = timezone.now()
            response.save()
            
            projection.status = 'RESPONDED'
            projection.advisor = request.user
            projection.save()
            
            messages.success(request, 'Respuesta enviada exitosamente')
            return redirect('client_portal:advisor_projections')
            
        except Exception as e:
            messages.error(request, f'Error al enviar el correo: {str(e)}')
            return redirect('client_portal:projection_detail', projection_id=projection_id)
    
    return render(request, 'client_portal/advisor/projection_detail.html', {
        'projection': projection
    })