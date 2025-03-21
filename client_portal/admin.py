from django.contrib import admin
from .models import SimpleProjection

@admin.register(SimpleProjection)
class SimpleProjectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'initial_amount', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
