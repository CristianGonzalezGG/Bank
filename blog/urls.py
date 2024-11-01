# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),  # Ruta a la página de inicio
    path('email-sent-success/', views.sent_email_success, name="email_sent_success"),
    path('send-email/', views.send_email_view, name='send_email'),
    path('register/', views.register_view, name='register'), 
    path('blog/', views.blog, name='blog'),
    path('tramites/', views.tramites, name='tramites'),
    path('pqr/', views.pqr, name="pqr"),
    path('negocios/', views.negocios, name='negocios'),
    path('educacion/', views.educacion, name='educacion'),
    path('asesores/', views.asesores, name='asesores'),
    path('get-card-info/', views.get_card_info, name='get_card_info'),
    path('clients/', views.client_list, name='client_list'),
    path('<int:id>/', views.client_detail, name='client_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/<int:id>/', views.loan_detail, name='loan_detail'),
    path('loans/create/', views.loan_create, name='loan_create'),
    path('loans/<int:id>/update/', views.loan_update, name='loan_update'),
    path('loans/<int:id>/delete/', views.loan_delete, name='loan_delete'),
]
