from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(email, code):
    try:
        subject = 'Código de Verificación para Préstamo'
        message = f'''
        Su código de verificación es: {code}
        
        Este código es válido por 30 minutos.
        Si no solicitó este código, por favor ignore este mensaje.
        
        No comparta este código con nadie.
        '''
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False 