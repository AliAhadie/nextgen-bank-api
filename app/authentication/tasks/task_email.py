from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_activation_email(id):

    activate_url= f"http://127.0.0.1:8000/activate/{id}"
    message = {
        'subject': 'Activate your account',
        'message': f'Click the link to activate your account: {activate_url}',
        

    }

    send_mail(message['subject'], message['message'], 'noreply@nextgenbank.com', ['test@example.com'])