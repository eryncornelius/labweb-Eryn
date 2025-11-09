from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'major', 'role', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'full_name': {'required': True},
            'major': {'required': True},
        }

    # Add validate and create methods from CustomUserSerializer
    def validate_email(self, value):
        email = value.lower()
        
        student_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@student\.prasetiyamulya\.ac\.id$')
        instructor_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@prasetiyamulya\.ac\.id$')
        
        if student_pattern.match(email) or instructor_pattern.match(email):
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email is already in use.")
            return email
        
        raise serializers.ValidationError("Email must be a valid student or instructor email address.")
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        email = validated_data['email'].lower()
        
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        role = "student" if domain == 'student.prasetiyamulya.ac.id' else "instructor"
            
        user = User.objects.create_user(
            email=email,
            username=username,
            full_name=validated_data['full_name'],
            major=validated_data.get('major', ''),
            role=role,
            password=validated_data['password']
        )
        return user
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'major', 'role', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'full_name': {'required': True},
            'major': {'required': True},
        }
        
    def validate_email(self, value):
        
        email = value.lower()
        
        student_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@student\.prasetiyamulya\.ac\.id$')
        instructor_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@prasetiyamulya\.ac\.id$')
        
        if student_pattern.match(email) or instructor_pattern.match(email):
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email is already in use.")
            return email
        
        raise serializers.ValidationError("Email must be a valid student or instructor email address.")
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        email = validated_data['email'].lower()
        
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        role = ""
        if domain == 'student.prasetiyamulya.ac.id':
            role = 'student'
        elif domain == 'prasetiyamulya.ac.id':
            role = 'instructor'
            
        user = User.objects.create(
            email=email,
            username=username,
            full_name=validated_data['full_name'],
            major=validated_data.get('major', ''),
            role=role,
        )
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        user.email = user.email.lower()

        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['full_name'] = user.full_name
        token['major'] = user.major
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        token_data = {
            'access': data['access'],
            'refresh': data['refresh'],
        }

        data.update({
            'email': self.user.email,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'major': self.user.major,
            'role': self.user.role,
            'token': token_data,
        })

        return data
