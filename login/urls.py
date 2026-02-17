from django.urls import path
from . import views

urlpatterns = [
    # When someone goes to website.com/login/, trigger the login_view
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('login-otp/', views.login_with_otp_view, name='login_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-register-otp/', views.verify_register_otp_view, name='verify_register_otp'),
    path('profile/', views.profile_view, name='profile'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    
]