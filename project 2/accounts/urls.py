from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
]