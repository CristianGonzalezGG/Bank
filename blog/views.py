from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from .models import Client, Account
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
def search_client(request):
    query = request.GET.get('cardId', '')  
    client = None
    accounts = []  # Inicializamos la lista de cuentas vacía

    if query:
        try:
            client = Client.objects.get(cardId=query)
            # Obtenemos todas las cuentas asociadas al cliente usando el related_name
            accounts = Account.objects.filter(client=client).select_related('client')
            
            # Para debugging
            print(f"Cliente encontrado: {client.name}")
            print(f"Número de cuentas encontradas: {accounts.count()}")
            
        except Client.DoesNotExist:
            client = None
        except Exception as e:
            print(f"Error al buscar cuentas: {str(e)}")

    context = {
        'client': client,
        'accounts': accounts,  # Pasamos las cuentas al contexto
        'query': query
    }

    return render(request, 'card_info.html', context)



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

def create_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog:client_list')  # Redirige a la lista de clientes

    else:
        form = ClientForm()

    return render(request, 'create_client.html', {'form': form})  # Asegúrate de que se está llamando al template correcto





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
                messages.success(request, f"Bienvenido, {username}!")
                # Redirigir a la página que el usuario intentaba acceder
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
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
def loan_detail(request, id):
    loan = get_object_or_404(Loan, id=id)
    return render(request, 'loan/loan_detail.html', {'loan': loan})

@login_required
def loan_create(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            try:
                loan = form.save(commit=False)
                loan.full_clean()
                loan.save()
                messages.success(request, 'Préstamo creado exitosamente.')
                return redirect('blog:loan_detail', id=loan.id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = LoanForm()
    return render(request, 'loan/loan_form.html', {'form': form})

@login_required
def loan_update(request, id):
    loan = get_object_or_404(Loan, id=id)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save()
            messages.success(request, 'Préstamo actualizado exitosamente.')
            return redirect('blog:loan_detail', id=loan.id)
    else:
        form = LoanForm(instance=loan)
    return render(request, 'loan/loan_form.html', {'form': form})

@login_required
def loan_delete(request, id):
    loan = get_object_or_404(Loan, id=id)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, 'Préstamo eliminado exitosamente.')
        return redirect('blog:loan_list')
    return render(request, 'loan/loan_confirm_delete.html', {'loan': loan})

@login_required
def generate_paz_y_salvo(request, id):
    loan = get_object_or_404(Loan, id=id)
    if loan.status != 'PAID':
        messages.error(request, 'El préstamo debe estar pagado completamente para generar el paz y salvo.')
        return redirect('blog:loan_detail', id=loan.id)
    
    try:
        pdf_path = loan.generate_certificate()
        if pdf_path:
            messages.success(request, 'Certificado generado y enviado por correo exitosamente.')
        else:
            messages.error(request, 'No se pudo generar el certificado.')
    except Exception as e:
        messages.error(request, f'Error al generar el certificado: {str(e)}')
    
    return redirect('blog:loan_detail', id=loan.id)

@login_required
def loan_payment(request, id):
    loan = get_object_or_404(Loan, id=id)
    
    if request.method == 'POST':
        payment_amount = request.POST.get('payment_amount')
        try:
            # Asegurar que el pago se procese como Decimal
            from decimal import Decimal
            payment_amount = Decimal(str(payment_amount))
            
            # Registrar el pago
            payment = loan.register_payment(payment_amount)
            
            # Verificar que payment sea un objeto Payment
            if hasattr(payment, 'amount'):
                messages.success(request, f'Pago de ${payment.amount} registrado correctamente.')
            else:
                # Por si acaso payment no es un objeto Payment
                messages.success(request, f'Pago de ${payment_amount} registrado correctamente.')
                
            return redirect('blog:loan_detail', id=loan.id)
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
    
    return render(request, 'loan/loan_payment.html', {'loan': loan})




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
    # Generate and save the code
    code = generate_2fa_code()
    expiry = timezone.now() + timedelta(minutes=10)
    
    # Limpiar códigos anteriores no verificados
    TwoFactorCode.objects.filter(
        user=user,
        is_verified=False
    ).delete()
    
    # Crear nuevo código
    TwoFactorCode.objects.create(
        user=user,
        code=code,
        expires_at=expiry
    )
    
    # Send email with the code
    send_mail(
        'Tu código de verificación',
        f'Tu código de verificación es: {code}\nEste código expirará en 10 minutos.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def verify_2fa(request):
    # Verificar si hay un usuario temporal en la sesión
    temp_user_id = request.session.get('temp_user_id')
    if not temp_user_id:
        messages.error(request, 'Por favor inicie sesión primero')
        return redirect('blog:login')
    
    try:
        user = User.objects.get(id=temp_user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('blog:login')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        
        valid_code = TwoFactorCode.objects.filter(
            user=user,
            code=code,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if valid_code:
            valid_code.is_verified = True
            valid_code.save()
            # Completar el login
            auth_login(request, user)
            # Marcar la sesión como verificada con 2FA
            request.session['2fa_verified'] = True
            # Limpiar el usuario temporal
            del request.session['temp_user_id']
            
            messages.success(request, '¡Verificación exitosa! Bienvenido.')
            return redirect('blog:home')
        else:
            messages.error(request, 'Código inválido o expirado')
    
    return render(request, 'blog/verify_2fa.html', {
        'email': user.email  # Mostrar el email al que se envió el código
    })

@login_required
def enable_2fa(request):
    # Get or create 2FA settings for user
    two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Enable 2FA
        two_factor_settings.is_enabled = True
        two_factor_settings.save()
        
        # Generate and send initial verification code
        send_2fa_code(request, request.user)
        
        messages.success(request, 'Two-factor authentication has been enabled.')
        return redirect('blog:verify_2fa')
    
    return render(request, 'blog/enable_2fa.html', {
        'two_factor_settings': two_factor_settings
    })

@login_required
def disable_2fa(request):
    try:
        two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Disable 2FA
            two_factor_settings.is_enabled = False
            two_factor_settings.save()
            
            # Clear 2FA verification from session
            if '2fa_verified' in request.session:
                del request.session['2fa_verified']
            
            messages.success(request, 'Two-factor authentication has been disabled.')
            return redirect('blog:home')
        
        return render(request, 'blog/disable_2fa.html', {
            'two_factor_settings': two_factor_settings
        })
        
    except UserTwoFactorSettings.DoesNotExist:
        messages.error(request, 'Two-factor authentication is not enabled.')
        return redirect('blog:home')

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
            # Obtener y limpiar los datos
            def clean_number(value):
                if isinstance(value, str):
                    return value.replace('$', '').replace(',', '').replace(' ', '')
                return value

            # Crear la proyección
            projection = SimpleProjection.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                initial_amount=Decimal(clean_number(request.POST.get('initial_amount', '0'))),
                term_days=int(request.POST.get('term_days', '0')),
                interest_rate=Decimal(clean_number(request.POST.get('interest_rate', '0'))),
                payment_type=request.POST.get('payment_type', 'maturity'),
                final_amount=Decimal(clean_number(request.POST.get('final_amount', '0'))),
                net_interest=Decimal(clean_number(request.POST.get('net_interest', '0'))),
                status='PENDING'
            )

            return JsonResponse({
                'success': True,
                'message': 'Proyección guardada exitosamente',
                'projection_id': projection.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar la proyección: {str(e)}'
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

@login_required
def advisor_projections(request):
    projections = SimpleProjection.objects.all().order_by('-created_at')
    return render(request, 'blog/advisor/projections.html', {
        'projections': projections
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

