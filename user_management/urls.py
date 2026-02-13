# urls.py
from django.urls import path
from .views import (
    UserRegistrationAPIView,
    CustomTokenObtainPairView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    SetNewPasswordAPIView
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('setpassword/<str:uidb64>/<str:token>/', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),

]