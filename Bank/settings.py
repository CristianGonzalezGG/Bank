# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'  # e.g., smtp.gmail.com for Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password-or-email-password'
DEFAULT_FROM_EMAIL = 'Banco El Dorado <noreply@bancoeldorado.com>'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'blog',  # Make sure your app is listed here
] 