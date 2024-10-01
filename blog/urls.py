from django.urls import path
from . import views
from .views import get_card_info
from django.conf import settings
from django.conf.urls.static import static
from .views import home
app_name = 'blog'

urlpatterns = [
    path('', home, name='home'),
    path('get-card-info/', get_card_info, name='get_card_info'),
    path('clients/', views.client_list, name='client_list'),
    path('<int:id>/', views.client_detail, name='client_detail'),
]
