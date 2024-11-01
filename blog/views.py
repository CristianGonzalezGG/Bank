from django.http import Http404
from django.contrib.auth import logout
from .models import Client, Account
import requests
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import EmailForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import EmailForm

@login_required
def send_email_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            # Extrae datos del formulario
            recipient_email = form.cleaned_data['recipient_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # URL del logo
            logo_url = f"{settings.STATIC_URL}images/logo.png"

            # Renderiza el contenido HTML del correo
            html_content = render_to_string('emails/send_email_template.html', {
                'logo_url': logo_url,
                'subject': subject,
                'message': message,
            })

            # Configura y envía el correo
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,  # Versión en texto plano
                from_email=settings.EMAIL_HOST_USER,
                to=[recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return redirect('/email-sent-success/')  # Redirige a la página de éxito
    else:
        form = EmailForm()

    return render(request, 'send_email_form.html', {'form': form})

@login_required
def sent_email_success(request):
    return render(request, 'email_sent_success.html')


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

@login_required
def client_list(request):
    clients = Client.objects.all() #Busca todos los clientes que se encuentren, sin verificar estatus
    
    return render(request, 'client/client_list.html', {'clients': clients})
@login_required
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
    loans = Loan.objects.filter(client=client)  # Obtener todos los préstamos del cliente

    # Suponiendo que deseas mostrar solo un monto total de deuda
    total_debt = sum(loan.amount for loan in loans)

    context = {
        'client': client,
        'total_debt': total_debt,
        'loans': loans,
    }
    
    return render(request, 'client/client_detail.html', {'client': client, 'account_number': account_number, 'model': model,})

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
                login(request, user)
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
from .models import Loan
from .forms import LoanForm
from django.contrib.auth.decorators import login_required

@login_required
def loan_list(request):
    loans = Loan.objects.all()
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
            form.save()
            return redirect('blog:loan_list')
    else:
        form = LoanForm()
    return render(request, 'loan/loan_form.html', {'form': form})

@login_required
def loan_update(request, id):
    loan = get_object_or_404(Loan, id=id)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect('blog:loan_detail', id=id)
    else:
        form = LoanForm(instance=loan)
    return render(request, 'loan/loan_form.html', {'form': form})

@login_required
def loan_delete(request, id):
    loan = get_object_or_404(Loan, id=id)
    if request.method == 'POST':
        loan.delete()
        return redirect('blog:loan_list')
    return render(request, 'loan/loan_confirm_delete.html', {'loan': loan})
