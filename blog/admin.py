from django.contrib import admin
from .models import Client, Account, Loan, Payment, Appointment, UserTwoFactorSettings, TwoFactorCode

# Registrar los modelos en el admin
admin.site.register(Client)
admin.site.register(Account)
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(Appointment)
admin.site.register(UserTwoFactorSettings)
admin.site.register(TwoFactorCode)
