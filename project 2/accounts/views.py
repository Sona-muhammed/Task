from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import OTPVerification
from .utils import send_otp_email
from django.contrib.auth import get_user_model

User = get_user_model()

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
                return redirect('accounts:verify_otp', user_id=user.id)  # Redirect to OTP verification page
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

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
        return redirect('accounts:signup')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        
        try:
            otp_obj = OTPVerification.objects.filter(user=user).latest('created_at')
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please register again.')
                user.delete()  # Delete unverified user
                return redirect('accounts:signup')
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
            return redirect('accounts:signup')
    
    return render(request, 'registration/verify_otp.html', {'user': user})