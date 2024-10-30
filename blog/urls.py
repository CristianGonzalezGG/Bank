from django.urls import path
from . import views
from .views import get_card_info, home, asesores, educacion, negocios, pqr, tramites, blog, register_view, login_view, sent_email_success
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, register_view  # Change home_view to home
from django.urls import path
from . import views


    


app_name = 'blog'

urlpatterns = [
    path('', home, name='home'),  # Ensure home is being used
    path('email-sent-success/', sent_email_success, name="email_sent_success"),
    path('send-email/', views.send_email_view, name='send_email'),
    path('registro/', register_view, name='register'),
    path('blog/', blog, name='blog'),
    path('tramites/', tramites, name='tramites'),
    path('pqr/', pqr, name="pqr"),
    path('negocios/', negocios, name='negocios'),
    path('educacion/', educacion, name='educacion'),
    path('asesores/', asesores, name='asesores'),
    path('get-card-info/', get_card_info, name='get_card_info'),
    path('clients/', views.client_list, name='client_list'),
    path('<int:id>/', views.client_detail, name='client_detail'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
