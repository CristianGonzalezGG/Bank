from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Make sure your blog app URLs are included
    path('', include('blog.urls')),  # Adjust the path as needed
    # Other URL patterns
] 