from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from .views import (
    create_client, search_clients,
    loan_list, loan_detail, loan_create, loan_update, loan_delete
)
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),  
    path('id-verification/', views.id_verification, name='id_verification'),
    path('email-sent-success/<int:client_id>/', views.sent_email_success, name="email_sent_success"),
    path('send-email/<int:client_id>/', views.send_email_view, name='send_email'),
    path('register/', views.register_view, name='register'), 
    path('blog/', views.blog, name='blog'),
    path('tramites/', views.tramites, name='tramites'),
    path('tramites-digitales/', views.tramites_digitales, name='tramites_digitales'),
    path('apertura-cuenta/', views.apertura_cuenta, name='apertura_cuenta'),
    path('negocios/', views.negocios, name='negocios'),
    path('educacion/', views.educacion, name='educacion'),
    path('asesores/', views.asesores, name='asesores'),
    path('check-bin/', views.bin_lookup, name='bin_lookup'),
    path('clients/', views.client_list, name='client_list'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tarjetas-debito/', views.tarjetas_debito, name='tarjetas_debito'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loan/create/', views.loan_create, name='loan_create'),
    path('loan/<int:pk>/', views.loan_detail, name='loan_detail'),
    path('loan/<int:pk>/update/', views.loan_update, name='loan_update'),
    path('loan/<int:pk>/delete/', views.loan_delete, name='loan_delete'),
    path('loan/<int:pk>/certificate/', views.generate_paz_y_salvo, name='generate_paz_y_salvo'),
    path('loan/<int:pk>/payment/', views.loan_payment, name='loan_payment'),
    path('create-client/', views.create_client, name='create_client'),
    path('create-account/<int:client_id>/', views.create_account, name='create_account'),
    path('appointments/search/', views.appointment_search_client, name='appointment_search_client'),
    path('appointments/create/<int:client_id>/', views.create_appointment, name='create_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('inversiones/', views.inversiones_view, name='inversiones'),
    path('seguridad/', views.seguridad, name='seguridad'),
    path('pqr/', views.pqr, name='pqr'),
    path('proyecciones/', views.proyecciones_view, name='proyecciones'),
    path('send-projection-email/', views.send_projection_email, name='send_projection_email'),
    path('search-clients/', views.search_clients, name='search_client'),  # Esta es la línea que agregamos
    
    # APIs
    path('api/search-clients/', views.search_clients, name='search_clients'),
    path('api/check-active-loan/<int:client_id>/', views.check_active_loan, name='check_active_loan'),
    path('api/send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('api/verify-code/', views.verify_code, name='verify_code'),
    path('api/security-questions/<int:client_id>/', views.get_security_questions, name='get_security_questions'),
    path('api/verify-security-answers/', views.verify_security_answers, name='verify_security_answers'),
    
    # Account management
    path('account/<int:account_id>/status/', views.update_account_status, name='update_account_status'),
    path('account/<int:account_id>/virtual-key/', views.update_virtual_key, name='update_virtual_key'),
    path('account/<int:account_id>/details/', views.get_account_details, name='get_account_details'),
    path('account/<int:account_id>/delete/', views.delete_account, name='delete_account'),
    path('account/<int:account_id>/manage/', views.manage_account, name='manage_account'),
    
    # Advisor routes
    path('advisor/projections/', views.advisor_projections, name='advisor_projections'),
    path('save_projection/', views.save_projection, name='save_projection'),
    path('projection/<int:projection_id>/mark-reviewed/', views.mark_projection_as_reviewed, name='mark_projection_reviewed'),
    path('projection/<int:projection_id>/contact/', views.contact_client, name='contact_client'),
    path('get-pending-projections/', views.get_pending_projections, name='get_pending_projections'),
    path('get-projection-detail/', views.view_projection_detail_api, name='get_projection_detail'),
    path('mark-projection-reviewed/', views.mark_projection_reviewed, name='mark_projection_reviewed'),
    path('contact-projection-client/', views.contact_projection_client, name='contact_projection_client'),
    path('delete-projection/', views.delete_projection, name='delete_projection'),
    path('projection/<int:projection_id>/', views.view_projection_detail, name='projection_detail'),
]