from django.contrib import admin
from .models import (
    Client, Account, Loan, Payment, Appointment, 
    UserTwoFactorSettings, TwoFactorCode, LoanVerification,
    SecurityQuestionTemplate, ClientSecurityQuestion  # Actualizados los nombres
)

@admin.register(SecurityQuestionTemplate)
class SecurityQuestionTemplateAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('question_text',)

@admin.register(ClientSecurityQuestion)
class ClientSecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ('client', 'question', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('client__name', 'question__question_text')
    raw_id_fields = ('client', 'question')

@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified']
    list_editable = ['is_verified']
    search_fields = ['user__username']
    list_filter = ['is_verified']

# Registrar los demás modelos que ya tenías
admin.site.register(Client)
admin.site.register(Account)
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(Appointment)
admin.site.register(UserTwoFactorSettings)
admin.site.register(LoanVerification)

