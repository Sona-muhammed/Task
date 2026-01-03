from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import OTPVerification
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


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
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def signup(request):
    """
    View for handling user registration.
    Creates user and sends OTP for email verification.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to database yet
            user.is_verified = False  # Mark as unverified
            user.save()  # Now save to database
            
            # Generate and store OTP
            otp_code = OTPVerification.generate_otp()
            otp_obj = OTPVerification.objects.create(user=user, otp_code=otp_code)
            
            # Send OTP to user's email
            if send_otp_email(user, otp_code):
                messages.success(request, f'Welcome {user.username}! Please check your email for the verification code.')
                return redirect('auth_module:verify_otp', user_id=user.id)  # Redirect to OTP verification page
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth_module/signup.html', {'form': form})


def verify_otp(request, user_id):
    """
    View for handling OTP verification.
    """
    try:
        user = User.objects.get(id=user_id)
        if user.is_verified:
            messages.info(request, 'Your account is already verified.')
            return redirect('dashboard')
    except User.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('auth_module:signup')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        
        try:
            otp_obj = OTPVerification.objects.filter(user=user).latest('created_at')
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please register again.')
                user.delete()  # Delete unverified user
                return redirect('auth_module:signup')
            elif otp_obj.otp_code == otp_input and not otp_obj.is_verified:
                # OTP is valid, activate user account
                user.is_verified = True
                user.save()
                otp_obj.is_verified = True
                otp_obj.save()
                
                # Log the user in
                login(request, user)
                messages.success(request, 'Your account has been verified successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please register again.')
            return redirect('auth_module:signup')
    
    return render(request, 'auth_module/verify_otp.html', {'user': user})


def login_view(request):
    """
    View for handling user login.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Using username field for email
            password = form.cleaned_data.get('password')
            
            # Authenticate using email
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_verified:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    
                    # Redirect to next page if provided, otherwise to dashboard
                    next_page = request.GET.get('next', 'dashboard')
                    return redirect(next_page)
                else:
                    messages.error(request, 'Please verify your email address before logging in.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'auth_module/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    View for handling user logout.
    """
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('auth_module:login')