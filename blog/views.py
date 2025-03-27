from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from .models import Client, Account, Loan, LoanVerification, SecurityQuestionTemplate, ClientSecurityQuestion, Payment, Projection
import requests
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import EmailForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Client
import cv2
import os
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import ClientForm
from .forms import ClientFormWithSecurity

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Client, Account
from .forms import AccountForm
from .models import Loan
from .forms import LoanForm
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import pdfkit
from decimal import Decimal, InvalidOperation
from django.http import StreamingHttpResponse
from django.db.models import F
import json
import time
from datetime import timedelta, datetime
from .models import Appointment
from .forms import AppointmentForm
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import UserTwoFactorSettings, TwoFactorCode
from django.contrib.auth.models import User
from .forms import PQRForm
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.conf import settings
import os
import uuid
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .forms import IDVerificationForm  # Asegúrate de importar el formulario
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from client_portal.models import ProjectionRequest, ProjectionResponse, SimpleProjection
from client_portal.forms import ProjectionForm
from django.db import transaction
from .utils import send_verification_email  # Agregar esta importación
from django.urls import reverse  # Agregar esta importación
from django.db.models import Q

def id_verification(request):
    if request.method == 'POST':
        form = IDVerificationForm(request.POST, request.FILES)  # Asegúrate de incluir request.FILES
        if form.is_valid():
            # Obtener los datos del formulario
            id_image = form.cleaned_data['id_image']
            document_type = form.cleaned_data['document_type']
            country = form.cleaned_data['country']
            document_number = form.cleaned_data['document_number']

            # URL de la API de ID Analyzer
            url = "https://api.idanalyzer.com/v1/verify"

            # Parámetros de la solicitud
            files = {'file': id_image}
            data = {
                'apikey': settings.ID_ANALYZER_API_KEY,
                'authenticate': 'true',  # Verificar autenticidad del documento
                'outputface': 'true',   # Extraer la cara del documento
                'document_type': document_type,  # Tipo de documento
                'country': country,  # País
                'document_number': document_number,  # Número de documento
            }

            # Hacer la solicitud a la API
            try:
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()  # Lanzar excepción si hay un error HTTP
                result = response.json()

                # Verificar si la respuesta es válida
                if result.get('error'):
                    return JsonResponse({'error': result['error']['message']}, status=400)

                # Devolver los resultados de la verificación
                return render(request, 'id_verification.html', {'result': result})

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Si el formulario no es válido, devuelve un error con más detalles
            return JsonResponse({'error': 'Formulario inválido', 'errors': form.errors}, status=400)

    else:
        # Si es una solicitud GET, muestra el formulario vacío
        form = IDVerificationForm()
        return render(request, 'id_verification.html', {'form': form})
def apertura_cuenta(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        identificacion = request.POST.get('identificacion')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        foto = request.FILES.get('foto')

        if not (nombre and identificacion and email and telefono and foto):
            return render(request, 'tramites_digitales.html', {'error': 'Todos los campos son obligatorios'})

        # Crear la carpeta si no existe
        folder_path = os.path.join(settings.MEDIA_ROOT, "solicitudes")
        os.makedirs(folder_path, exist_ok=True)

        # Generar un nombre único para la imagen
        file_extension = foto.name.split('.')[-1]  # Obtener la extensión (png, jpg, etc.)
        filename = f"{uuid.uuid4().hex}.{file_extension}"  # Nombre aleatorio único
        foto_path = os.path.join(folder_path, filename)

        # Guardar la imagen en la carpeta
        with open(foto_path, 'wb+') as destination:
            for chunk in foto.chunks():
                destination.write(chunk)

        # Enviar correo con la imagen adjunta
        subject = "Nueva Solicitud de Apertura de Cuenta"
        message = f"""
        Se ha recibido una nueva solicitud de apertura de cuenta.

        🏦 Banco El Dorado 🏦
        
        📌 Nombre: {nombre}
        📌 Identificación: {identificacion}
        📌 Correo Electrónico: {email}
        📌 Teléfono: {telefono}

        📎 Se adjunta la foto del solicitante.
        """
        
        email_message = EmailMessage(
            subject,
            message,
            settings.PQR_RECIPIENT_EMAIL,
            [settings.EMAIL_HOST_USER],
        )
        email_message.attach_file(foto_path)
        email_message.send()

        return render(request, 'tramites_digitales.html', {'success': 'Solicitud enviada correctamente'})

    return render(request, 'tramites_digitales.html')


@login_required
def search_clients(request):
    query = request.GET.get('q', '')
    if len(query) < 3:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Ingrese al menos 3 caracteres para buscar'}, status=400)
        else:
            messages.warning(request, 'Ingrese al menos 3 caracteres para buscar')
            return redirect('blog:client_list')
    
    clients = Client.objects.filter(
        Q(name__icontains=query) | 
        Q(cardId__icontains=query)
    )[:10]  # Limitamos a 10 resultados
    
    results = []
    for client in clients:
        results.append({
            'id': client.id,
            'name': client.name,
            'cardId': client.cardId,
            'email': client.email,
            'url': reverse('blog:client_detail', args=[client.id])
        })
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(results, safe=False)
    else:
        # Para solicitudes no AJAX, renderizar una plantilla con los resultados
        return render(request, 'client/search_results.html', {'results': results, 'query': query})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Client, Account
from .forms import AccountForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from .models import Client, Account
from .forms import AccountForm

@login_required
def create_account(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            try:
                account = form.save(commit=False)
                account.client = client

                # Validar límites de cuenta antes de guardar
                account.validate_account_limit(client)

                # Configurar campos específicos según el tipo de cuenta
                if account.account_type.startswith('SAVINGS_'):
                    account.balance = form.cleaned_data.get('initial_deposit', 0)
                    account.virtual_key = account.generate_virtual_key()
                    
                    if account.account_type == 'SAVINGS_NOMINA':
                        account.company_nit = form.cleaned_data.get('company_nit')
                        account.company_name = form.cleaned_data.get('company_name')
                
                elif account.account_type == 'CHECKING':
                    account.credit_limit = form.cleaned_data.get('credit_limit')
                    account.cvv = account.generate_cvv()
                    account.expiration_date = account.generate_expiration_date()
                
                account.save()
                
                success_message = [
                    f'Cuenta creada exitosamente.',
                    f'Número de cuenta: {account.numberAccount}'
                ]

                if account.virtual_key:
                    success_message.append(f'Clave virtual: {account.virtual_key}')
                if account.cvv:
                    success_message.append(f'CVV: {account.cvv}')
                if account.expiration_date:
                    success_message.append(f'Fecha de vencimiento: {account.expiration_date.strftime("%m/%Y")}')

                messages.success(request, '\n'.join(success_message))
                return redirect('blog:client_detail', id=client_id)
                
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AccountForm()
    
    context = {
        'form': form,
        'client': client,
        'existing_accounts': Account.objects.filter(client=client),
        'can_create_savings': not Account.objects.filter(
            client=client,
            account_type__in=['SAVINGS_NORMAL', 'SAVINGS_NOMINA', 'SAVINGS_AMIGA']
        ).exists(),
        'can_create_checking': not Account.objects.filter(
            client=client,
            account_type='CHECKING'
        ).exists(),
    }
    
    return render(request, 'account/create_account.html', context)
from django.shortcuts import render

import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .forms import ClientForm
from .models import Client

from django.shortcuts import render, redirect
from .forms import ClientForm
from django.shortcuts import render, redirect
from .forms import ClientForm

@login_required
def create_client(request):
    if request.method == "POST":
        form = ClientFormWithSecurity(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear el cliente
                    client = form.save()

                    # Crear las preguntas de seguridad
                    for i in range(3):
                        ClientSecurityQuestion.objects.create(
                            client=client,
                            question=form.cleaned_data[f'security_question_{i}'],
                            answer=form.cleaned_data[f'security_answer_{i}']
                        )

                    messages.success(request, f'Cliente {client.name} creado exitosamente.')
                    return redirect('blog:client_detail', id=client.id)

            except Exception as e:
                messages.error(request, f'Error al crear el cliente: {str(e)}')
        else:
            # Imprimir errores para debugging
            print("Errores del formulario:", form.errors)
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ClientFormWithSecurity()

    return render(request, 'client/create_client.html', {'form': form})

def send_security_questions_email(client):
    """Envía un correo al cliente con sus preguntas de seguridad"""
    subject = 'Confirmación de Registro - Preguntas de Seguridad'
    context = {
        'client': client,
        'questions': ClientSecurityQuestion.objects.filter(client=client)
    }
    html_message = render_to_string('emails/security_questions_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Error sending security questions email to {client.email}: {str(e)}")

@login_required
def send_email_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            try:
                # Crear el contenido HTML del correo
                html_content = render_to_string('emails/email_template.html', {
                    'client': client,
                    'message': message
                })
                
                # Crear el correo
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,  # Versión texto plano
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[client.email]
                )
                
                # Adjuntar versión HTML
                email.attach_alternative(html_content, "text/html")
                
                # Enviar el correo
                email.send()
                
                messages.success(request, 'Correo enviado exitosamente')
                return redirect('blog:email_sent_success', client_id=client.id)
            
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {str(e)}')
    else:
        form = EmailForm()
    
    return render(request, 'emails/send_email_form.html', {
        'form': form,
        'client': client
    })

@login_required
def sent_email_success(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'email_sent_success.html', {
        'client_email': client.email,
        'client_id': client_id
    })


def home(request):
    return render(request, 'index.html')
@login_required
def asesores(request):
    return render(request, 'asesores.html')
def educacion(request):
    return render(request, 'educacion_financiera.html')
def negocios(request):
    return render(request, 'negocios.html')
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from datetime import datetime

def generate_radicado():
    """
    Genera un número de radicado único para las PQR
    Formato: PQR-YYYYMMDD-XXXXX (donde X es un número aleatorio)
    """
    # Obtener la fecha actual en formato YYYYMMDD
    fecha = datetime.now().strftime('%Y%m%d')
    
    # Generar 5 dígitos aleatorios
    digitos = ''.join(random.choices(string.digits, k=5))
    
    # Crear el número de radicado
    radicado = f"PQR-{fecha}-{digitos}"
    
    return radicado

def pqr(request):
    """Vista para mostrar y procesar el formulario de PQR con un correo más estilizado."""
    if request.method == 'POST':
        form = PQRForm(request.POST)
        if form.is_valid():
            # Obtener datos validados del formulario
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            documento = form.cleaned_data['documento']
            telefono = form.cleaned_data['telefono']
            tipo = form.cleaned_data['tipo']
            asunto = form.cleaned_data['asunto']
            descripcion = form.cleaned_data['descripcion']
            
            # Generar número de radicado
            radicado = generate_radicado()
            
            # Construir el mensaje de correo en HTML
            mensaje_html = format_html(f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">Nueva Solicitud PQR - Banco El Dorado</h2>
                    <hr style="border: 1px solid #ddd;">
                    
                    <p><strong>Número de Radicado:</strong> {radicado}</p>
                    <p><strong>Fecha y Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                    <h3 style="color: #2980b9;">Información del Solicitante:</h3>
                    <p><strong>Nombre Completo:</strong> {nombre}</p>
                    <p><strong>Correo Electrónico:</strong> {email}</p>
                    <p><strong>Documento de Identidad:</strong> {documento}</p>
                    <p><strong>Teléfono de Contacto:</strong> {telefono}</p>

                    <h3 style="color: #2980b9;">Detalles de la Solicitud:</h3>
                    <p><strong>Tipo de Solicitud:</strong> {tipo}</p>
                    <p><strong>Asunto:</strong> {asunto}</p>

                    <h3 style="color: #c0392b;">Descripción:</h3>
                    <p style="background: #f8f9fa; padding: 10px; border-left: 4px solid #c0392b;">{descripcion}</p>

                    <hr style="border: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #7f8c8d;">
                        Este correo ha sido generado automáticamente por el sistema de PQR del Banco El Dorado.<br>
                        Por favor, no responda a este mensaje.
                    </p>
                </div>
            """)

            try:
                # Enviar correo
                send_mail(
                    subject=f'[PQR-{radicado}] {tipo}: {asunto}',
                    message='Este correo no admite formato HTML. Por favor, visualícelo en un cliente de correo compatible.',
                    html_message=mensaje_html,
                    from_email=settings.PQR_RECIPIENT_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                )

                # Mensaje de éxito y redirección
                messages.success(request, f'Su solicitud ha sido enviada exitosamente. Su número de radicado es: {radicado}')
                return render(request, 'pqr.html', {'form': PQRForm(), 'radicado': radicado, 'envio_exitoso': True})

            except Exception as e:
                messages.error(request, f'Ocurrió un error al enviar su solicitud: {str(e)}')

    return render(request, 'pqr.html', {'form': PQRForm()})

def tramites(request):
    return render(request, 'tramites_digitales.html')
def blog(request):
    return render(request, 'blog.html')

@login_required


def bin_lookup(request):
    card_data = None
    error = None

    if request.method == 'POST':
        bin_number = request.POST.get('bin_number')
        if bin_number:
            # URL de la API
            api_key = settings.BIN_CHECKER_API_KEY
            url = f"https://api.bincodes.com/bin/?format=json&api_key={api_key}&bin={bin_number}"
            
            # Hacer la solicitud a la API
            try:
                response = requests.get(url)
                response.raise_for_status()  # Asegura que no haya error HTTP
                data = response.json()
                print(data)
                # Verifica si la respuesta contiene datos válidos
                if data.get("valid") == "true":
                    card_data = data
                else:
                    error = "El BIN ingresado no es válido o no se encuentra en la base de datos."

            except requests.exceptions.RequestException as e:
                error = f"Ocurrió un error al hacer la solicitud: {str(e)}"

    return render(request, 'card_info.html', {'card_data': card_data, 'error': error})


@login_required
def client_list(request):
    # Usar select_related y prefetch_related para optimizar las consultas
    clients = Client.objects.prefetch_related(
        'accounts'
    ).order_by('-created_at')
    
    return render(request, 'client/client_list.html', {
        'clients': clients
    })





from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Client, Account, Appointment

@login_required
def client_detail(request, id):
    client = get_object_or_404(Client, id=id)
    
    # Obtener todas las cuentas asociadas al cliente usando el related_name
    accounts = Account.objects.filter(client=client)
    
    # Obtener todas las citas asociadas al cliente
    appointments = Appointment.objects.filter(client=client).order_by('-date', '-time')
    
    context = {
        'client': client,
        'accounts': accounts,
        'appointments': appointments,  # Agregar las citas al contexto
    }
    
    return render(request, 'client/client_detail.html', context)
# Vista de registro de usuario
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registro exitoso, has iniciado sesión.")
            return redirect("blog:home")
        else:
            messages.error(request, "Error al registrarse. Verifica los datos.")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

# Vista de login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Iniciar proceso 2FA
                try:
                    two_factor_settings = UserTwoFactorSettings.objects.get(user=user)
                except UserTwoFactorSettings.DoesNotExist:
                    two_factor_settings = UserTwoFactorSettings.objects.create(user=user, is_enabled=True)

                if two_factor_settings.is_enabled:
                    # Enviar código 2FA
                    if send_2fa_code(request, user):
                        messages.success(request, "Por favor verifica el código enviado a tu correo.")
                        return redirect('blog:verify_2fa')
                    else:
                        messages.error(request, "Error al enviar el código de verificación.")
                        logout(request)
                        return redirect('blog:login')
                
                return redirect('blog:home')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request) 
    return redirect('blog:home') 

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Loan
from .forms import LoanForm

@login_required
def loan_list(request):
    loans = Loan.objects.all().select_related('client')
    return render(request, 'loan/loan_list.html', {'loans': loans})

@login_required
def loan_detail(request, pk):
    try:
        loan = get_object_or_404(Loan, pk=pk)
        
        # Verificar que el usuario tenga permiso para ver este préstamo
        if not request.user.is_staff and loan.created_by != request.user:
            raise PermissionError("No tiene permiso para ver este préstamo")

        # Obtener pagos si existen
        try:
            payments = Payment.objects.filter(loan=loan).order_by('-payment_date')
        except Payment.DoesNotExist:
            payments = []

        context = {
            'loan': loan,
            'client': loan.client,
            'payments': payments,
            'monthly_payment': loan.monthly_payment,
            'remaining_balance': loan.remaining_balance,
            'next_payment_date': loan.next_payment_date,
        }
        
        return render(request, 'loan/loan_detail.html', context)
        
    except PermissionError as e:
        messages.error(request, str(e))
        return redirect('loan_list')

@login_required
def loan_create(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            client = get_object_or_404(Client, id=data['client_id'])
            
            # Verificar la existencia de una verificación válida
            verification = LoanVerification.objects.filter(
                client=client,
                is_verified=True,
                security_answers_verified=True,
                expires_at__gt=timezone.now()
            ).order_by('-created_at').first()

            if not verification:
                return JsonResponse({
                    'success': False,
                    'error': 'La verificación ha expirado o las respuestas de seguridad son incorrectas.'
                }, status=400)

            # Crear el préstamo
            loan = Loan.objects.create(
                client=client,
                amount=Decimal(data['amount']),
                interest_rate=Decimal(data['interest_rate']),
                repayment_term=int(data['repayment_term']),
                status='PENDING',
                created_by=request.user,
                verification=verification,
                start_date=timezone.now().date()
            )

            # Calcular saldo y cuotas
            loan.remaining_balance = loan.amount
            loan.monthly_payment = loan.calculate_monthly_payment()
            loan.next_payment_date = loan.start_date + timedelta(days=30)
            loan.save()

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('blog:loan_detail', args=[loan.id])
            })

        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            print("Error inesperado:", str(e))
            return JsonResponse({
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            }, status=500)

    # Para solicitudes GET normales, renderizar la plantilla
    client_id = request.GET.get('client_id')
    initial_data = {}
    
    if client_id:
        try:
            client = Client.objects.get(id=client_id)
            initial_data['client'] = client
        except Client.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
    
    return render(request, 'loan/loan_form.html', {'initial_data': initial_data})

def tarjetas_debito(request):
       return render(request, 'blog/tarjetas_debito.html')

@login_required
def loan_update(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save()
            messages.success(request, 'Préstamo actualizado exitosamente.')
            return redirect('blog:loan_detail', pk=loan.id)
    else:
        form = LoanForm(instance=loan)
    return render(request, 'loan/loan_form.html', {'form': form})

@login_required
def loan_delete(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, 'Préstamo eliminado exitosamente.')
        return redirect('blog:loan_list')
    return render(request, 'loan/loan_confirm_delete.html', {'loan': loan})

@login_required
def generate_paz_y_salvo(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.status != 'PAID':
        messages.error(request, 'El préstamo debe estar pagado completamente para generar el paz y salvo.')
        return redirect('blog:loan_detail', pk=loan.id)
    
    try:
        pdf_path = loan.generate_certificate()
        if pdf_path:
            messages.success(request, 'Certificado generado y enviado por correo exitosamente.')
        else:
            messages.error(request, 'No se pudo generar el certificado.')
    except Exception as e:
        messages.error(request, f'Error al generar el certificado: {str(e)}')
    
    return redirect('blog:loan_detail', pk=loan.id)

@login_required
def loan_payment(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    
    if not request.user.is_staff and loan.created_by != request.user:
        messages.error(request, "No tiene permiso para registrar pagos en este préstamo")
        return redirect('blog:loan_list')

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            
            if amount <= 0:
                raise ValueError("El monto del pago debe ser mayor que cero")
            
            if amount > loan.remaining_balance:
                raise ValueError("El monto del pago no puede ser mayor al saldo pendiente")

            # Crear el pago
            payment = Payment.objects.create(
                loan=loan,
                amount=amount,
                created_by=request.user,
                balance_after=loan.remaining_balance - amount
            )

            # Actualizar el saldo del préstamo
            loan.remaining_balance -= amount
            loan.last_payment_date = timezone.now().date()
            
            # Si el saldo llega a 0, marcar como pagado y generar paz y salvo
            if loan.remaining_balance <= 0:
                loan.status = 'PAID'
                loan.remaining_balance = Decimal('0')
                loan.save()
                
                # Generar y enviar el paz y salvo
                try:
                    pdf_path = loan.generate_certificate()
                    if pdf_path:
                        messages.success(request, "Préstamo pagado completamente. El certificado de paz y salvo ha sido enviado al correo del cliente.")
                    else:
                        messages.warning(request, "Préstamo pagado pero hubo un error al generar el certificado de paz y salvo.")
                except Exception as e:
                    messages.error(request, f"Error al generar el certificado: {str(e)}")
            else:
                # Actualizar próxima fecha de pago solo si aún hay saldo
                loan.next_payment_date = loan.last_payment_date + timezone.timedelta(days=30)
                loan.save()
                messages.success(request, "Pago registrado exitosamente")

            return redirect('blog:loan_detail', pk=loan.id)

        except (ValueError, InvalidOperation) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al procesar el pago: {str(e)}")

    context = {
        'loan': loan,
        'client': loan.client,
        'payments': Payment.objects.filter(loan=loan).order_by('-payment_date'),
        'remaining_balance': loan.remaining_balance,
    }
    
    return render(request, 'loan/loan_payment.html', context)




@login_required
def appointment_search_client(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        try:
            client = Client.objects.get(cardId=card_id)
            return redirect('blog:create_appointment', client_id=client.id)
        except Client.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
    
    return render(request, 'appointments/search_client.html')

@login_required
def create_appointment(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = client
            appointment.save()
            
            messages.success(request, 'Cita agendada exitosamente')
            return redirect('blog:appointment_list')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'client': client
    })

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('date', 'time')
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments
    })

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada exitosamente')
            return redirect('blog:appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'appointments/appointment_detail.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'CANCELLED'
    appointment.save()
    messages.success(request, 'Cita cancelada exitosamente')
    return redirect('blog:appointment_list')

def generate_2fa_code():
    return ''.join(random.choices(string.digits, k=6))

def send_2fa_code(request, user):
    """
    Genera y envía un código 2FA por correo electrónico
    """
    try:
        # Generar nuevo código
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expiry_time = timezone.now() + timezone.timedelta(minutes=10)
        
        # Guardar el código en la base de datos
        TwoFactorCode.objects.filter(user=user).delete()  # Eliminar códigos anteriores
        two_factor_code = TwoFactorCode.objects.create(
            user=user,
            code=code,
            expires_at=expiry_time
        )
        
        # Preparar el contexto para el email
        context = {
            'user': user,
            'code': code,
            'expiry_minutes': 10
        }
        
        # Renderizar el template HTML
        html_content = render_to_string('emails/2fa_code.html', context)  # Asegúrate de que esta ruta sea correcta
        text_content = strip_tags(html_content)
        
        # Enviar el email
        try:
            email = EmailMultiAlternatives(
                subject='Código de Verificación - Banco El Dorado',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            print(f"2FA code sent successfully to {user.email}")  # Debug log
            return True
            
        except Exception as email_error:
            print(f"Error sending email: {str(email_error)}")  # Debug log
            two_factor_code.delete()  # Eliminar el código si falla el envío
            return False
            
    except Exception as e:
        print(f"Error in send_2fa_code: {str(e)}")  # Debug log
        return False

@login_required
def verify_2fa(request):
    """
    Vista para verificar el código 2FA
    """
    # Si ya está verificado, redirigir a la página original
    if request.session.get('2fa_verified', False):
        next_url = request.session.get('next_url', 'blog:home')
        return redirect(next_url)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            stored_code = TwoFactorCode.objects.filter(
                user=request.user,
                is_verified=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            if stored_code and stored_code.code == code:
                # Código válido
                stored_code.is_verified = True
                stored_code.save()
                
                # Marcar como verificado en la sesión
                request.session['2fa_verified'] = True
                
                # Redirigir a la página original
                next_url = request.session.get('next_url', 'blog:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Código inválido o expirado.')
        except TwoFactorCode.DoesNotExist:
            messages.error(request, 'No hay código de verificación válido.')
    
    # Enviar nuevo código si no hay uno válido
    if not TwoFactorCode.objects.filter(
        user=request.user,
        is_verified=False,
        expires_at__gt=timezone.now()
    ).exists():
        if send_2fa_code(request, request.user):
            messages.info(request, 'Se ha enviado un nuevo código a su correo.')
        else:
            messages.error(request, 'Error al enviar el código. Por favor intente nuevamente.')
    
    return render(request, 'blog/verify_2fa.html')

@login_required
def enable_2fa(request):
    """
    Vista para habilitar 2FA
    """
    try:
        two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
    except UserTwoFactorSettings.DoesNotExist:
        two_factor_settings = UserTwoFactorSettings.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Enviar código de verificación
        if send_2fa_code(request, request.user):
            two_factor_settings.is_enabled = True
            two_factor_settings.save()
            messages.success(request, 'Se ha enviado un código de verificación a su correo.')
            return redirect('blog:verify_2fa')
        else:
            messages.error(request, 'Error al enviar el código de verificación.')
    
    return render(request, 'blog/enable_2fa.html', {
        'two_factor_settings': two_factor_settings
    })

def inversiones_view(request):
    """Vista pública para la página de inversiones"""
    return render(request, 'inversiones.html')

def proyecciones_view(request):
    """Vista pública para la página de proyecciones"""
    return render(request, 'proyecciones.html')

def tramites_digitales(request):
    """Vista pública para la página de trámites digitales"""
    return render(request, 'tramites_digitales.html')

def seguridad(request):
    """Vista pública para la página de seguridad"""
    return render(request, 'seguridad.html')

def send_projection_email(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            # Get data from the POST request
            data = json.loads(request.body)
            client_name = data.get('clientName', '')
            client_email = data.get('clientEmail', '')
            projection_data = data.get('projectionData', {})
            
            if not client_email:
                return JsonResponse({'success': False, 'message': 'Se requiere correo electrónico del cliente'})
            
            # Create the email context
            context = {
                'client_name': client_name,
                'advisor_name': request.user.get_full_name() or request.user.username,
                'projection': projection_data,
                'date': projection_data.get('date', ''),
            }
            
            # Render the email template
            html_message = render_to_string('email_projection.html', context)
            plain_message = strip_tags(html_message)
            
            # Send the email
            email = EmailMessage(
                subject=f'Proyección CDT - Banco El Dorado',
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[client_email],
                reply_to=[request.user.email or settings.DEFAULT_FROM_EMAIL]
            )
            email.content_subtype = "html"  # Set the content type to HTML
            email.send()
            
            return JsonResponse({'success': True, 'message': f'Proyección enviada a {client_email}'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al enviar email: {str(e)}'})
            
    return JsonResponse({'success': False, 'message': 'Método no permitido o usuario no autenticado'})

@require_http_methods(["POST"])
@login_required
def update_account_status(request, account_id):
    try:
        account = get_object_or_404(Account, id=account_id)
        data = json.loads(request.body)
        account.is_active = data.get('is_active', account.is_active)
        account.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Estado de cuenta actualizado',
            'is_active': account.is_active
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@require_http_methods(["POST"])
@login_required
def update_virtual_key(request, account_id):
    try:
        account = get_object_or_404(Account, id=account_id)
        data = json.loads(request.body)
        new_key = data.get('new_key')
        
        if not new_key or len(new_key) < 6:
            raise ValidationError('La clave virtual debe tener al menos 6 caracteres')
            
        account.virtual_password = new_key
        account.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Clave virtual actualizada exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
@login_required
def get_account_details(request, account_id):
    try:
        account = get_object_or_404(Account, id=account_id)
        return JsonResponse({
            'success': True,
            'data': {
                'id': account.id,
                'number': account.numberAccount,
                'type': account.get_account_type_display(),
                'balance': float(account.balance),
                'interest_rate': float(account.interest_rate),
                'is_active': account.is_active,
                'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'management_fee': float(account.management_fee) if account.management_fee else 0,
                'credit_limit': float(account.credit_limit) if account.credit_limit else 0
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_account(request, account_id):
    try:
        account = get_object_or_404(Account, id=account_id)
        account.delete()
        return JsonResponse({
            'success': True,
            'message': 'Cuenta eliminada exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def manage_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'update_status':
                new_status = request.POST.get('status') == 'true'
                account.is_active = new_status
                account.save()
                messages.success(request, 'Estado de cuenta actualizado exitosamente')
                
            elif action == 'update_virtual_key':
                new_key = request.POST.get('new_virtual_key')
                confirm_key = request.POST.get('confirm_virtual_key')
                
                if new_key != confirm_key:
                    raise ValidationError('Las claves no coinciden')
                if len(new_key) < 6:
                    raise ValidationError('La clave debe tener al menos 6 caracteres')
                    
                account.virtual_password = new_key
                account.save()
                messages.success(request, 'Clave virtual actualizada exitosamente')
                
            elif action == 'delete':
                client_id = account.client.id
                account.delete()
                messages.success(request, 'Cuenta eliminada exitosamente')
                return redirect('blog:client_detail', id=client_id)
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('blog:manage_account', account_id=account_id)
    
    # Obtener historial de transacciones (si existe)
    transactions = []  # Aquí puedes agregar la lógica para obtener transacciones si las tienes
    
    context = {
        'account': account,
        'transactions': transactions,
    }
    
    return render(request, 'account/manage_account.html', context)

@csrf_exempt
def save_projection(request):
    if request.method == 'POST':
        try:
            # Access form data from request.POST
            client_name = request.POST.get('name', '')
            client_email = request.POST.get('email', '')
            initial_amount_str = request.POST.get('initial_amount', '0')
            final_amount_str = request.POST.get('final_amount', '0')
            net_interest_str = request.POST.get('net_interest', '0')
            interest_rate_str = request.POST.get('interest_rate', '0')
            term_days = request.POST.get('term_days', '0')
            payment_type = request.POST.get('payment_type', '')

            # Print received values for debugging
            print(f"Received values: initial={initial_amount_str}, final={final_amount_str}, interest={interest_rate_str}, net={net_interest_str}")

            # Clean and convert numeric fields to Decimal
            try:
                # Handle different decimal formats by normalizing to simple decimal string
                # Replace comma with empty string if it's used as thousand separator (1,000.00 -> 1000.00)
                # Replace comma with period if it's used as decimal separator (1000,00 -> 1000.00)
                def clean_decimal(value):
                    # First, remove any currency symbols, spaces, and other non-numeric characters
                    # except for period and comma
                    value = ''.join(c for c in value if c.isdigit() or c in ['.', ','])
                    
                    # Count the occurrences of period and comma
                    periods = value.count('.')
                    commas = value.count(',')
                    
                    # Case 1: Only periods as thousand separators (1.000.000 -> 1000000)
                    if periods > 1 and commas == 0:
                        value = value.replace('.', '')
                    # Case 2: Only commas as thousand separators (1,000,000 -> 1000000)
                    elif commas > 1 and periods == 0:
                        value = value.replace(',', '')
                    # Case 3: Period as decimal and comma as thousand (1,000.00 -> 1000.00)
                    elif periods == 1 and commas > 0:
                        value = value.replace(',', '')
                    # Case 4: Comma as decimal and period as thousand (1.000,00 -> 1000.00)
                    elif commas == 1 and periods > 0:
                        value = value.replace('.', '')
                        value = value.replace(',', '.')
                    # Case 5: Single comma used as decimal separator (1000,00 -> 1000.00)
                    elif commas == 1 and periods == 0:
                        value = value.replace(',', '.')
                    
                    # Default case: If no changes were needed, return as is
                    return value

                # Clean and convert each value
                initial_amount = Decimal(clean_decimal(initial_amount_str))
                final_amount = Decimal(clean_decimal(final_amount_str))
                net_interest = Decimal(clean_decimal(net_interest_str))
                interest_rate = Decimal(clean_decimal(interest_rate_str))
                
                # Print cleaned values for debugging
                print(f"Cleaned values: initial={initial_amount}, final={final_amount}, interest={interest_rate}, net={net_interest}")
                
            except (InvalidOperation, ValueError, TypeError) as e:
                print(f"Conversion error: {str(e)}")
                return JsonResponse({'success': False, 'message': f'Error converting values: {str(e)}'}, status=400)

            # Ensure all required fields are present and valid
            if not client_name or not client_email:
                return JsonResponse({'success': False, 'message': 'Missing client name or email'}, status=400)
            
            if initial_amount <= 0 or interest_rate <= 0:
                return JsonResponse({'success': False, 'message': 'Amount and interest rate must be positive'}, status=400)

            try:
                term_days = int(term_days)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid term days value'}, status=400)

            # Save the projection with a simplified approach
            projection = Projection(
                client_name=client_name,
                client_email=client_email,
                initial_amount=initial_amount,
                final_amount=final_amount,
                net_interest=net_interest,
                interest_rate=interest_rate,
                term_days=term_days,
                payment_type=payment_type
            )
            projection.save()

            return JsonResponse({'success': True, 'message': 'Projection saved successfully'})

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def advisor_projections(request):
    projections = Projection.objects.all().order_by('-created_at')
    return render(request, 'advisor/projections.html', {
        'projections': projections,
    })

def mark_projection_as_reviewed(request, projection_id):
    if request.method == 'POST':
        try:
            projection = get_object_or_404(SimpleProjection, id=projection_id)
            projection.status = 'REVIEWED'
            projection.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def contact_client(request, projection_id):
    projection = get_object_or_404(SimpleProjection, id=projection_id)
    
    if request.method == 'POST':
        try:
            # Preparar el contexto para el template
            context = {
                'subject': request.POST.get('subject', 'Seguimiento de su Proyección CDT'),
                'message': request.POST.get('message', ''),
                'client_name': projection.name,
                'projection': {
                    'amount': f"${projection.initial_amount:,.2f}",
                    'term': projection.term_days,
                    'rate': projection.interest_rate
                }
            }

            try:
                # Intentar renderizar el template
                html_message = render_to_string('emails/send_email_template.html', context)
            except Exception as template_error:
                return JsonResponse({
                    'success': False,
                    'error': f"Error al renderizar el template: {str(template_error)}"
                })

            try:
                # Intentar enviar el correo
                send_mail(
                    subject=context['subject'],
                    message='',  # Versión texto plano
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[projection.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as email_error:
                return JsonResponse({
                    'success': False,
                    'error': f"Error al enviar el correo: {str(email_error)}"
                })

            # Actualizar estado
            projection.status = 'CONTACTED'
            projection.save()

            return render(request, 'blog/email_sent_success.html', {
                'client_email': projection.email,
                'client_id': projection_id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    # Para GET request, mostrar el formulario
    return render(request, 'blog/send_email_form.html', {
        'projection': projection,
        'form': {
            'to_email': projection.email,
            'subject': 'Seguimiento de su Proyección CDT - Banco El Dorado',
            'message': f'Hemos revisado su solicitud de proyección CDT por un monto de ${projection.initial_amount:,.2f} a {projection.term_days} días.'
        }
    })

@login_required
def check_active_loan(request, client_id):
    """API endpoint para verificar préstamos activos"""
    try:
        # Verificar si el cliente existe
        client = get_object_or_404(Client, id=client_id)
        
        # Verificar préstamos activos
        has_active_loan = Loan.objects.filter(
            client_id=client_id,
            status__in=['PENDING', 'ACTIVE']
        ).exists()
        
        # Si tiene préstamo activo, obtener los detalles
        active_loan = None
        if has_active_loan:
            loan = Loan.objects.get(
                client_id=client_id,
                status__in=['PENDING', 'ACTIVE']
            )
            active_loan = {
                'amount': str(loan.amount),
                'start_date': loan.start_date.strftime('%Y-%m-%d'),
                'remaining_balance': str(loan.remaining_balance),
                'status': loan.get_status_display()
            }
        
        return JsonResponse({
            'success': True,
            'hasActiveLoan': has_active_loan,
            'activeLoan': active_loan,
            'client': {
                'name': client.name,
                'email': client.email
            }
        })
        
    except Client.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
def send_verification_code(request):
    try:
        data = json.loads(request.body)
        client_id = data.get('clientId')
        
        if not client_id:
            return JsonResponse({'success': False, 'error': 'ID de cliente no proporcionado'})

        client = get_object_or_404(Client, id=client_id)
        
        # Generar código de 6 dígitos
        verification_code = ''.join(random.choices('0123456789', k=6))
        
        # Crear nueva verificación
        verification = LoanVerification.objects.create(
            client=client,
            code=verification_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )

        # Enviar el código por correo
        if send_verification_email(client.email, verification_code):
            return JsonResponse({'success': True})
        else:
            verification.delete()  # Si falla el envío, eliminar la verificación
            return JsonResponse({
                'success': False, 
                'error': 'Error al enviar el código de verificación'
            })

    except Exception as e:
        print(f"Error en send_verification_code: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def verify_code(request):
    try:
        data = json.loads(request.body)
        client_id = data.get('clientId')
        submitted_code = data.get('code')

        if not client_id or not submitted_code:
            return JsonResponse({
                'success': False, 
                'error': 'Datos incompletos'
            })

        # Buscar verificación válida más reciente
        verification = LoanVerification.objects.filter(
            client_id=client_id,
            code=submitted_code,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            return JsonResponse({
                'success': False,
                'error': 'Código inválido o expirado'
            })

        # Marcar como verificado
        verification.is_verified = True
        verification.save()

        return JsonResponse({'success': True})

    except Exception as e:
        print(f"Error en verify_code: {str(e)}")  # Para depuración
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_security_questions(request, client_id):
    try:
        answers = ClientSecurityQuestion.objects.filter(client_id=client_id).select_related('question')
        
        if not answers.exists():
            return JsonResponse({'error': 'No questions found'}, status=404)
            
        questions_data = [{
            'id': answer.question.id,  # Use 'id'
            'question': answer.question.question_text  # Use 'question'
        } for answer in answers]
        
        return JsonResponse(questions_data, safe=False)  # Return a direct array
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def verify_security_answers(request):
    try:
        # Log the incoming request body
        print("Incoming request body:", request.body)

        data = json.loads(request.body)
        client_id = data.get('client_id')
        answers = data.get('answers', [])

        if not client_id or not answers:
            return JsonResponse({
                'success': False,
                'message': 'Datos incompletos'
            }, status=400)

        client = get_object_or_404(Client, id=client_id)
        
        # Obtener las preguntas del cliente
        client_questions = ClientSecurityQuestion.objects.filter(client=client)
        
        if not client_questions.exists():
            return JsonResponse({
                'success': False,
                'message': 'No se encontraron preguntas de seguridad para el cliente'
            }, status=400)

        # Verificar las respuestas
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            provided_answer = answer_data.get('answer', '').strip()
            
            try:
                question = client_questions.get(question__id=question_id)
                if not question.verify_answer(provided_answer):
                    return JsonResponse({
                        'success': False,
                        'message': 'Respuestas de seguridad incorrectas'
                    }, status=400)
            except ClientSecurityQuestion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'Pregunta de seguridad con ID {question_id} no encontrada'
                }, status=400)

        # Marcar la verificación como completada
        verification = LoanVerification.objects.filter(
            client=client,
            is_verified=True,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if verification:
            verification.security_answers_verified = True
            verification.save()

        return JsonResponse({
            'success': True,
            'message': 'Respuestas verificadas correctamente'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        print(f"Error en verify_security_answers: {str(e)}")  # Para debugging
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar las respuestas: {str(e)}'
        }, status=500)

@login_required
def create_loan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client = get_object_or_404(Client, id=data['client_id'])
            
            # Verificar la existencia de una verificación válida
            verification = LoanVerification.objects.filter(
                client=client,
                is_verified=True,
                security_answers_verified=True,  # Ensure answers are verified
                expires_at__gt=timezone.now()
            ).order_by('-created_at').first()

            if not verification:
                return JsonResponse({
                    'success': False,
                    'error': 'La verificación ha expirado o las respuestas de seguridad son incorrectas.'
                }, status=400)

            # Crear el préstamo
            loan = Loan.objects.create(
                client=client,
                amount=Decimal(data['amount']),
                interest_rate=Decimal(data['interest_rate']),
                repayment_term=int(data['repayment_term']),
                status='PENDING',
                created_by=request.user,
                verification=verification,
                start_date=timezone.now().date()
            )

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('blog:loan_detail', args=[loan.id])
            })

        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            print("Error inesperado:", str(e))
            return JsonResponse({
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            }, status=500)

    return render(request, 'loan/loan_form.html')

@login_required
def disable_2fa(request):
    """View to handle 2FA disabling"""
    try:
        two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Disable 2FA
            two_factor_settings.is_enabled = False
            two_factor_settings.save()
            messages.success(request, 'Two-factor authentication has been disabled.')
            return redirect('blog:home')
            
        return render(request, 'blog/disable_2fa.html', {
            'two_factor_settings': two_factor_settings
        })
        
    except UserTwoFactorSettings.DoesNotExist:
        messages.error(request, 'Two-factor authentication settings not found.')
        return redirect('blog:home')

@login_required
def active_loan_details(request, client_id):
    try:
        client = get_object_or_404(Client, id=client_id)
        loan = Loan.objects.filter(client=client, status__in=['PENDING', 'ACTIVE']).first()
        
        if not loan:
            return JsonResponse({'success': False, 'message': 'No active loan found for this client.'}, status=404)
        
        loan_details = {
            'amount': str(loan.amount),
            'interest_rate': str(loan.interest_rate),
            'repayment_term': loan.repayment_term,
            'start_date': loan.start_date.strftime('%Y-%m-%d'),
            'remaining_balance': str(loan.remaining_balance),
            'status': loan.status,
        }
        
        return JsonResponse({'success': True, 'loan_details': loan_details})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def get_pending_projections(request):
    """Obtener lista de proyecciones pendientes"""
    projections = Projection.objects.all().order_by('-created_at')
    data = []
    
    for proj in projections:
        data.append({
            'id': proj.id,
            'client_name': proj.client_name,
            'client_email': proj.client_email,
            'initial_amount': str(proj.initial_amount),
            'term_days': proj.term_days,
            'interest_rate': str(proj.interest_rate),
            'payment_type': proj.payment_type,
            'final_amount': str(proj.final_amount),
            'net_interest': str(proj.net_interest),
            'created_at': proj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': getattr(proj, 'status', 'PENDING')
        })
    
    return JsonResponse(data, safe=False)

@login_required
def view_projection_detail(request, projection_id):
    """Vista para mostrar detalles de una proyección"""
    try:
        projection = Projection.objects.get(id=projection_id)
        response_history = []  # Puedes implementar una lógica para obtener historial de respuestas si existe
        
        context = {
            'projection': projection,
            'response_history': response_history
        }
        return render(request, 'advisor/projection_detail.html', context)
    except Projection.DoesNotExist:
        messages.error(request, 'La proyección solicitada no existe.')
        return redirect('blog:advisor_projections')

@csrf_exempt
@login_required
def mark_projection_reviewed(request):
    """Marcar una proyección como revisada"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        projection_id = data.get('id')
        
        projection = Projection.objects.get(id=projection_id)
        # Si el modelo no tiene status, asegúrate de que lo tenga en la definición del modelo
        if hasattr(projection, 'status'):
            projection.status = 'REVIEWED'
            projection.save()
            
        return JsonResponse({'success': True})
    except Projection.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Proyección no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@login_required
def contact_projection_client(request):
    """Enviar email al cliente y marcar como contactado"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        projection_id = data.get('id')
        subject = data.get('subject')
        message = data.get('message')
        
        projection = Projection.objects.get(id=projection_id)
        
        # Aquí implementarías el envío del email
        # Por ahora, solo marcamos como contactado
        if hasattr(projection, 'status'):
            projection.status = 'CONTACTED'
            projection.save()
        
        return JsonResponse({'success': True})
    except Projection.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Proyección no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@login_required
def delete_projection(request):
    """Eliminar una proyección"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        projection_id = data.get('id')
        
        projection = Projection.objects.get(id=projection_id)
        projection.delete()
        
        return JsonResponse({'success': True})
    except Projection.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Proyección no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@login_required
def view_projection_detail_api(request):
    """API para obtener detalles de una proyección"""
    projection_id = request.GET.get('id')
    
    try:
        projection = Projection.objects.get(id=projection_id)
        data = {
            'success': True,
            'projection': {
                'id': projection.id,
                'client_name': projection.client_name,
                'client_email': projection.client_email,
                'initial_amount': str(projection.initial_amount),
                'term_days': projection.term_days,
                'interest_rate': str(projection.interest_rate),
                'payment_type': projection.payment_type,
                'final_amount': str(projection.final_amount),
                'net_interest': str(projection.net_interest),
                'created_at': projection.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': getattr(projection, 'status', 'PENDING')
            }
        }
        return JsonResponse(data)
    except Projection.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Proyección no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

