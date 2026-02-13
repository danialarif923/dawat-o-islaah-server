import os
from rest_framework import generics, permissions, status
from django.http import Http404
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User
from .utils import send_forget_password_email
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    SetNewPasswordSerializer
)
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from dawat_o_islaah.settings import *


class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except serializers.ValidationError as e:
            # Customize error messages
            if 'No active account found' in str(e):
                raise serializers.ValidationError({
                    "email": "User not found",
                    "password": "Invalid credentials"
                })
            raise e

        # Add custom user data
        user = self.user
        data.update({
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        })
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                user = User.objects.get(email=request.data['email'])
                
            return response
            
        except User.DoesNotExist:
            raise Http404("User not found")
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ChangePasswordAPIView(generics.GenericAPIView):

    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ForgotPasswordAPIView(generics.GenericAPIView):

        def post(self, request):
         
            email = request.data.get("email")

            try:
                user = get_object_or_404(User, email=email)
            except Exception:
                return Response(data={'success': False, 'message': 'This email does not exist in our system'}, status=status.HTTP_404_NOT_FOUND)
            
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site =CURRENT_SITE
            absurl = f'{current_site}setpassword/{uidb64}/{token}/'
            send_forget_password_email(user.first_name,email,absurl)
            return Response({'success': 'Password Reset Email Sent', 'message': 'We have sent you an email with a link to reset your password. Please check your inbox and follow the instructions to reset your password.'}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):
    
    def patch(self, request,**kwargs):
        
        serializer=SetNewPasswordSerializer(data=request.data,context={'uid':kwargs['uidb64'],'token':kwargs['token']})
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)