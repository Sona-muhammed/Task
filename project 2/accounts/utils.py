from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_otp_email(user, otp_code):
    """
    Send OTP code to user's email address
    """
    subject = 'Your OTP Verification Code'
    
    # Create HTML message
    html_message = render_to_string('emails/otp_email.html', {
        'user': user,
        'otp_code': otp_code,
        'expiry_time': '10 minutes'
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False