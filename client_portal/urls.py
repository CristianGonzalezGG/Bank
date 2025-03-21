from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'client_portal'

urlpatterns = [
    # URLs temporales que redirigen a las vistas de blog
    path('login/', lambda request: redirect('blog:login'), name='client_login'),
    path('register/', lambda request: redirect('blog:register'), name='client_register'),
    path('save-projection/', views.save_projection, name='save_projection'),
    path('advisor/projections/', views.advisor_projections, name='advisor_projections'),
    path('advisor/projection/<int:projection_id>/', views.projection_detail, name='projection_detail'),
]