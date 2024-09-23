from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('clients/', views.client_list, name='client_list'),
    path('<int:id>/', views.client_detail, name='client_detail'),
]
