import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from django.contrib.auth import authenticate


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
       
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not authenticate(email=user.email, password=value):
            raise serializers.ValidationError("Incorrect old password.")
        return value
    
    def validate(self, attrs):
       
       old_password = attrs.get('old_password')
       new_password = attrs.get('new_password')
       special_characters = r'[!@#$%^&*()\-_=+{}\[\]|;:"<>,.?/]'
       special_characters_count = len(re.findall(special_characters, new_password))
       
       if old_password == new_password:
           raise serializers.ValidationError({
                 'Error': "New password must be different from the old password."
              })
       elif len(new_password) < 8:
         raise serializers.ValidationError({'Error':"Password must be at least 8 characters long."})
       
       elif special_characters_count < 1:
         raise serializers.ValidationError({'Error':"Password must contain at least 1 special character."})
       
       return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)



class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
  

    def validate(self, attrs):   
        password = attrs.get('password')
        token = self.context['token']
        uidb64 =self.context['uid']
        id = force_str(urlsafe_base64_decode(uidb64))
        
        try:
                user = get_object_or_404(User, id=id)
        except Exception:
                return Response(data={'success': False, 'message': 'This email does not exist in our system'}, status=status.HTTP_404_NOT_FOUND)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({'Error':"The reset link is invalid"})
        
        special_characters = r'[!@#$%^&*()\-_=+{}\[\]|;:"<>,.?/]'
        special_characters_count = len(re.findall(special_characters, password))
        
        if len(password) < 8:
            raise serializers.ValidationError({'Error':"Password must be at least 8 characters long."})
        
        elif special_characters_count < 1:
            raise serializers.ValidationError({'Error':"Password must contain at least 1 special character."})
        
        user.set_password(password)
        user.save()
        return user