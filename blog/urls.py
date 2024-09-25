from django.urls import path
from . import views
from .views import get_card_info
app_name = 'blog'

urlpatterns = [
    path('get-card-info/', get_card_info, name='get_card_info'),
    path('clients/', views.client_list, name='client_list'),
    path('<int:id>/', views.client_detail, name='client_detail'),
]
