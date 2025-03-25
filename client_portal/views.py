from django.urls import path
from . import views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ProjectionRequest, ProjectionResponse, Projection
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import json
from decimal import Decimal, InvalidOperation
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from django.views.decorators.csrf import csrf_exempt

app_name = 'client_portal'  # Añade esta línea

urlpatterns = [

]

@csrf_exempt
def save_projection(request):
    if request.method == 'POST':
        try:
            # Access form data from request.POST
            client_name = request.POST.get('name')
            client_email = request.POST.get('email')
            initial_amount = request.POST.get('initial_amount')
            final_amount = request.POST.get('final_amount')
            net_interest = request.POST.get('net_interest')
            interest_rate = request.POST.get('interest_rate')
            term_days = request.POST.get('term_days')
            payment_type = request.POST.get('payment_type')

            # Convert numeric fields to Decimal
            initial_amount = Decimal(initial_amount.replace('.', '').replace(',', '.'))
            final_amount = Decimal(final_amount.replace('.', '').replace(',', '.'))
            net_interest = Decimal(net_interest.replace('.', '').replace(',', '.'))
            interest_rate = Decimal(interest_rate.replace('.', '').replace(',', '.'))

            # Ensure all required fields are present
            if not all([client_name, client_email, initial_amount, final_amount, net_interest, interest_rate, term_days, payment_type]):
                return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

            # Save the projection
            projection = Projection.objects.create(
                client_name=client_name,
                client_email=client_email,
                initial_amount=initial_amount,
                final_amount=final_amount,
                net_interest=net_interest,
                interest_rate=interest_rate,
                term_days=int(term_days),
                payment_type=payment_type
            )

            return JsonResponse({'success': True, 'message': 'Projection saved successfully'})

        except (InvalidOperation, ValueError) as e:
            return JsonResponse({'success': False, 'message': f'Error converting values: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

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