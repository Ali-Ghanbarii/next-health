from django.urls import path
from . import views

urlpatterns = [
    # API for logging in or registering
    path('api/login-or-register/', views.LoginOrRegisterView.as_view(), name='login_or_register'),
    
    # API for OTP generation
    path('api/otp/generate/', views.OTPGenerateView.as_view(), name='otp_generate'),
    
    # API for OTP verification
    path('api/otp-verify/', views.OTPVerifyView.as_view(), name='otp_verify'),
]
