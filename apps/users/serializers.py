from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model.
    
    Provides basic user information for read operations.
    Used in nested serializers for events and other resources.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for new user registration.
    
    Handles user creation with proper password hashing.
    Requires minimum password length of 6 characters.
    """

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        """Create a new user with hashed password.
        
        Args:
            validated_data: Dictionary containing validated user data.
            
        Returns:
            User: The newly created user instance.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication.
    
    Validates user credentials and ensures the account is active.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials and account status.
        
        Args:
            data: Dictionary containing email and password.
            
        Returns:
            dict: Validated data with authenticated user instance.
            
        Raises:
            ValidationError: If credentials are invalid or account is deactivated.
        """
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated')
            data['user'] = user
        else:
            raise serializers.ValidationError('Email and password are required')

        return data
