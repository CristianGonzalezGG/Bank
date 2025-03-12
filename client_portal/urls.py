from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'client_portal'

urlpatterns = [
    # URLs temporales que redirigen a las vistas de blog
    path('login/', lambda request: redirect('blog:login'), name='client_login'),
    path('register/', lambda request: redirect('blog:register'), name='client_register'),
]