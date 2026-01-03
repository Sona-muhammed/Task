from django.urls import path
from . import views

app_name = 'auth_module'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]