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
from decimal import Decimal
from django.http import StreamingHttpResponse
from django.db.models import F
import json
import time
from datetime import timedelta
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

@login_required
def search_client(request):
    query = request.GET.get('cardId', '')  
    client = None
    account = None

    if query:
        try:
            client = Client.objects.get(cardId=query)
            if hasattr(client, 'account'):
                account = client.account
        except Client.DoesNotExist:
            client = None

    return render(request, 'card_info.html', {'client': client, 'account': account, 'query': query})

@login_required
def create_account(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    
    # Verificar si el cliente ya tiene una cuenta
    if hasattr(client, 'account'):
        messages.error(request, "Este cliente ya tiene una cuenta.")
        return redirect('blog:client_detail', id=client_id)

    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.client = client
            
            # Establecer la tasa de interés según el tipo de cuenta
            if account.account_type == 'SAVINGS':
                account.interest_rate = 2.5
            elif account.account_type == 'FIXED':
                account.interest_rate = 4.0
            else:
                account.interest_rate = 0.5
                
            account.balance = form.cleaned_data['initial_deposit']
            account.save()

            messages.success(
                request, 
                f'Cuenta creada exitosamente. Número de cuenta: {account.numberAccount}'
            )
            
            return redirect('blog:client_detail', id=client_id)
        else:
            messages.error(request, "Error al crear la cuenta. Por favor, verifique los datos.")
    else:
        form = AccountForm()

    return render(request, 'account/create_account.html', {
        'form': form,
        'client': client
    })

from django.shortcuts import render

def create_client(request):
    return render(request, 'create_client.html')


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
@login_required
def educacion(request):
    return render(request, 'educacion_financiera.html')
@login_required
def negocios(request):
    return render(request, 'negocios.html')

def pqr(request):
    return render(request, 'pqr.html')
@login_required
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
    clients = Client.objects.all().prefetch_related('account')
    return render(request, 'client/client_list.html', {'clients': clients})
def create_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES)  # Si capturas imagen, usa request.FILES
        if form.is_valid():
            form.save()
            return redirect('blog:client_list')  # Redirigir a la lista de clientes
    else:
        form = ClientForm()
    return render(request, 'create_client.html', {'form': form})

@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de la imagen
            image_data = request.POST.get('imageData')
            client_id = request.POST.get('clientId')
            
            if not image_data or not client_id:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)
            
            # Obtener el cliente
            client = get_object_or_404(Client, id=client_id)
            
            # Convertir la data URI a imagen
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Crear un archivo temporal
            from django.core.files.base import ContentFile
            image_content = ContentFile(base64.b64decode(imgstr))
            
            # Generar un nombre único para el archivo
            import uuid
            file_name = f'client_photo_{uuid.uuid4()}.{ext}'
            
            # Guardar la imagen
            client.imageSave.save(file_name, image_content, save=True)
            
            return JsonResponse({
                'success': True,
                'message': 'Imagen guardada correctamente',
                'image_url': client.imageSave.url
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def client_detail(request, id):
    client = get_object_or_404(Client, id=id)
    account_number = client.get_account_number()
    appointments = client.appointments.all()  # Obtener todas las citas del cliente
    
    # Obtener el modelo de la tarjeta si existe
    try:
        account = Account.objects.get(client=client)
        model = {
            'client': client,
            'account': account,
            'account_number': account_number,
        }
    except Account.DoesNotExist:
        model = {
            'client': client,
            'account_number': 'No Account',
        }

    context = {
        'client': client,
        'account_number': account_number,
        'model': model,
        'appointments': appointments,  # Pasar las citas al contexto
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
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.email:  # Si el usuario tiene email, forzar 2FA
                    # Guardar el usuario en la sesión temporalmente
                    request.session['temp_user_id'] = user.id
                    # Generar y enviar código 2FA
                    send_2fa_code(request, user)
                    messages.info(request, "Por favor ingrese el código de verificación enviado a su correo.")
                    return redirect('blog:verify_2fa')
                else:
                    # Si no tiene email, login normal
                    auth_login(request, user)
                    messages.success(request, f"Bienvenido, {username}")
                    return redirect("blog:home")
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
            loan = form.save()
            messages.success(request, 'Préstamo creado exitosamente.')
            return redirect('blog:loan_detail', id=loan.id)
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
        payment_amount = Decimal(request.POST.get('payment_amount', 0))
        
        if payment_amount <= 0:
            messages.error(request, 'El monto del pago debe ser mayor a 0.')
        elif payment_amount > loan.remaining_balance:
            messages.error(request, 'El monto del pago no puede ser mayor al saldo restante.')
        else:
            loan.register_payment(payment_amount)
            messages.success(request, f'Pago de ${payment_amount} registrado exitosamente.')
            
            if loan.status == 'PAID':
                messages.info(request, 'El préstamo ha sido pagado en su totalidad.')
            
            return redirect('blog:loan_detail', id=loan.id)
    
    return render(request, 'loan/loan_payment.html', {'loan': loan})

@login_required
def financial_goals(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.client = request.user.client
            goal.save()
            return redirect('blog:financial_goals')
    
    goals = FinancialGoal.objects.filter(client=request.user.client)
    form = FinancialGoalForm()
    return render(request, 'financial/goals.html', {'goals': goals, 'form': form})

@login_required
def transactions(request):
    account = request.user.client.account
    transactions = Transaction.objects.filter(account=account)
    
    # Filtros
    category = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if category:
        transactions = transactions.filter(category=category)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
        
    context = {
        'transactions': transactions,
        'categories': Transaction.objects.values_list('category', flat=True).distinct(),
        'total_income': transactions.filter(type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_expenses': transactions.filter(type='WITHDRAWAL').aggregate(Sum('amount'))['amount__sum'] or 0
    }
    return render(request, 'transactions/list.html', context)

@login_required
def notifications(request):
    """Vista para mostrar todas las notificaciones del usuario"""
    notifications = Notification.objects.filter(client=request.user.client)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es una petición AJAX, devolver JSON
        data = [{
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'type': notif.type,
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            'read': notif.read
        } for notif in notifications]
        return JsonResponse(data, safe=False)
    
    # Si no es AJAX, renderizar template
    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })

@login_required
def notifications_stream(request):
    """Vista para Stream de notificaciones en tiempo real"""
    def event_stream():
        while True:
            # Verificar nuevas notificaciones
            notifications = Notification.objects.filter(
                client=request.user.client,
                read=False
            ).order_by('-created_at')[:5]
            
            for notification in notifications:
                data = {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'time': notification.created_at.strftime('%H:%M')
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            time.sleep(10)  # Esperar 10 segundos antes de la siguiente verificación
    
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

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
