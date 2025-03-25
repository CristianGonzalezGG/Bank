# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # O tu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo@gmail.com'  # Tu correo
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_aplicacion'  # Tu contraseña de aplicación
DEFAULT_FROM_EMAIL = 'tu_correo@gmail.com'  # El correo que aparecerá como remitente 