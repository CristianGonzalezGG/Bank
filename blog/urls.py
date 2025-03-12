# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from .views import (
    create_client, capture_image, search_client,
    loan_list, loan_detail, loan_create, loan_update, loan_delete
)

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),  
    path('email-sent-success/', views.sent_email_success, name="email_sent_success"),
    path('send-email/', views.send_email_view, name='send_email'),
    path('register/', views.register_view, name='register'), 
    path('blog/', views.blog, name='blog'),
    path('tramites/', views.tramites, name='tramites'),
    path('tramites/', views.tramites_digitales, name='tramites_digitales'),
    
    path('negocios/', views.negocios, name='negocios'),
    path('educacion/', views.educacion, name='educacion'),
    path('asesores/', views.asesores, name='asesores'),
    path('check-bin/', views.bin_lookup, name='bin_lookup'),
    path('clients/', views.client_list, name='client_list'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loan/create/', views.loan_create, name='loan_create'),
    path('loan/<int:id>/', views.loan_detail, name='loan_detail'),
    path('loan/<int:id>/update/', views.loan_update, name='loan_update'),
    path('loan/<int:id>/delete/', views.loan_delete, name='loan_delete'),
    path('loan/<int:id>/certificate/', views.generate_paz_y_salvo, name='generate_paz_y_salvo'),
    path('loan/<int:id>/payment/', views.loan_payment, name='loan_payment'),
    path('create-client/', views.create_client, name='create_client'),
    path('capture-image/', views.capture_image, name='capture_image'),
    path('search-client/', views.search_client, name='search_client'),
    path('create-account/<int:client_id>/', views.create_account, name='create_account'),
    path('client/<int:client_id>/send-email/', views.send_email_view, name='send_email'),
    path('client/<int:client_id>/email-sent-success/', views.sent_email_success, name='email_sent_success'),
    path('appointments/search/', views.appointment_search_client, name='appointment_search_client'),
    path('appointments/create/<int:client_id>/', views.create_appointment, name='create_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('inversiones/', views.inversiones_view, name='inversiones'),
    path('seguridad/', views.seguridad_view, name='seguridad'),
    path('pqr/', views.pqr, name='pqr'),
]
