from django.shortcuts import render
from django.http import Http404

# Create your views here.
from .models import Client, Account
from django.shortcuts import render
import requests

from django.shortcuts import render
import requests

from django.shortcuts import render
import requests

from django.shortcuts import render

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import EmailForm

def sent_email_success(request):
    return render(request, 'email_sent_success.html')

def send_email_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            recipient_email = form.cleaned_data['recipient_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']


            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # Sender's email
                [recipient_email],  # Recipient's email
                fail_silently=False,
            )
            return redirect('/email-sent-success/')  # Redirect to a success page
    else:
        form = EmailForm()

    return render(request, 'send_email_form.html', {'form': form})

def home(request):
    return render(request, 'index.html')

def asesores(request):
    return render(request, 'asesores.html')

def educacion(request):
    return render(request, 'educacion_financiera.html')

def negocios(request):
    return render(request, 'negocios.html')
def pqr(request):
    return render(request, 'pqr.html')
def tramites(request):
    return render(request, 'tramites_digitales.html')
def blog(request):
    return render(request, 'blog.html')


def get_card_info(request):
    card_data = None
    error = None

    if request.method == 'POST':
        bin_number = request.POST.get('bin_number')

        # Validar si el número BIN tiene entre 6 y 8 dígitos
        if not bin_number or len(bin_number) < 6 or len(bin_number) > 8:
            error = 'El número BIN debe tener entre 6 y 8 dígitos.'
        else:
            try:
                url = f"https://lookup.binlist.net/{bin_number}"
                # Añadimos un timeout para evitar esperas infinitas y controlamos las excepciones
                response = requests.get(url, timeout=10)
                
                # Si la respuesta es 200, todo está bien
                if response.status_code == 200:
                    card_data = response.json()  # Convertir la respuesta a un diccionario
                elif response.status_code == 404:
                    error = f'No se encontró información para el BIN {bin_number}.'
                elif response.status_code == 429:
                    error = 'Has excedido el límite de peticiones. Inténtalo más tarde.'
                else:
                    error = f'Ocurrió un error. Código de estado: {response.status_code}'
            except requests.Timeout:
                error = 'La solicitud a la API ha superado el tiempo de espera. Inténtalo de nuevo más tarde.'
            except requests.RequestException as e:
                error = f'Ocurrió un error de conexión: {str(e)}'
    
    # Renderizamos el template con los datos de la tarjeta o el mensaje de error
    return render(request, 'card_info.html', {'card_data': card_data, 'error': error})


def client_list(request):
    clients = Client.objects.all() #Busca todos los clientes que se encuentren, sin verificar estatus
    
    return render(request, 'client/client_list.html', {'clients': clients})
def client_detail(request, id):
    try:
        client = Client.objects.get(id=id)
        # Verificar si el cliente tiene una cuenta asociada
        if hasattr(client, 'account'):
            account_number = client.account.numberAccount  # Acceder al número de cuenta correctamente
            model = client.account.get_account_type_display
        else:
            account_number = 'No Account'  # Si no tiene una cuenta
    except Client.DoesNotExist:
        raise Http404("Client not found")
    
    return render(request, 'client/client_detail.html', {'client': client, 'account_number': account_number, 'model': model,})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirigir a la página de inicio
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'index.html')  # Renderiza tu template de login (index.html)

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})  # Renderiza tu template de registro (register.html)
