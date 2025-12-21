from typing import Dict, Any
from django.contrib.auth import authenticate
from .models import User, MAX_NAME_LENGTH, INVITATION_PRIVACY_MAX_LENGTH, MAX_EMAIL_LENGTH
from rest_framework.serializers import (
    Serializer,
    CharField,
    EmailField,
    SerializerMethodField,
    IntegerField,
    DateTimeField,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

PASSWORD_MIN_LENGTH = 6

class UserSerializer(Serializer):
    """Serializer for User model.

    Provides basic user information for read operations.
    Used in nested serializers for events and other resources.
    """

    id: IntegerField = IntegerField(read_only=True)
    email: EmailField = EmailField(read_only=True)
    name: CharField = CharField(read_only=True, max_length=MAX_NAME_LENGTH)
    created_at: DateTimeField = DateTimeField(read_only=True)
    invitation_privacy: CharField = CharField(read_only=True, max_length=INVITATION_PRIVACY_MAX_LENGTH)


class UserRegistrationSerializer(Serializer):
    """Serializer for new user registration.

    Handles user creation with proper password hashing.
    Requires minimum password length of 6 characters and password confirmation.
    """

    email: EmailField = EmailField(required=True, help_text="User email address")
    name: CharField = CharField(required=True, max_length=MAX_NAME_LENGTH, help_text="User display name")
    password: CharField = CharField(
        write_only=True,
        required=True,
        min_length=PASSWORD_MIN_LENGTH,
        style={"input_type": "password"},
        help_text=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long",
    )
    password_confirm: CharField = CharField(
        write_only=True,
        required=True,
        min_length=PASSWORD_MIN_LENGTH,
        style={"input_type": "password"},
        help_text="Confirm your password",
    )

    def validate_email(self, value: str) -> str:
        """Validate email is unique and properly formatted.

        Args:
            value: Email address to validate.

        Returns:
            str: Validated email address in lowercase.

        Raises:
            ValidationError: If email already exists.
        """
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise ValidationError("User with this email already exists")
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate password confirmation matches.

        Args:
            data: Dictionary containing all validated field data.

        Returns:
            dict: Validated data without password_confirm field.

        Raises:
            ValidationError: If passwords don't match.
        """
        if data.get("password") != data.get("password_confirm"):
            raise ValidationError({"password_confirm": "Passwords do not match"})
        data.pop("password_confirm")
        return data

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user with hashed password.

        Args:
            validated_data: Dictionary containing validated user data.

        Returns:
            User: The newly created user instance.
        """
        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(Serializer):
    """Serializer for user authentication.

    Validates user credentials and ensures the account is active.
    """

    email: EmailField = EmailField(help_text="User email address")
    password: CharField = CharField(
        write_only=True, style={"input_type": "password"}, help_text="User password"
    )

    def validate_email(self, value: str) -> str:
        """Normalize email to lowercase.

        Args:
            value: Email address.

        Returns:
            str: Normalized email address.
        """
        return value.lower().strip()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user credentials and account status.

        Args:
            data: Dictionary containing email and password.

        Returns:
            dict: Validated data with authenticated user instance.

        Raises:
            ValidationError: If credentials are invalid or account is deactivated.
        """
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValidationError("Email and password are required")

        user = authenticate(email=email, password=password)

        if not user:
            raise ValidationError(
                "Invalid email or password. Please check your credentials."
            )

        if not user.is_active:
            raise ValidationError(
                "This account has been deactivated. Please contact support."
            )

        data["user"] = user
        return data


class AuthTokenSerializer(Serializer):
    """Serializer for authentication response with tokens.

    Returns user data along with JWT access and refresh tokens.
    """

    user: UserSerializer = UserSerializer(read_only=True)
    tokens: SerializerMethodField = SerializerMethodField()

    def get_tokens(self, obj: Dict[str, Any]) -> Dict[str, str]:
        """Generate JWT tokens for the user.

        Args:
            obj: Dictionary containing user instance.

        Returns:
            dict: Access and refresh tokens.
        """
        user = obj.get("user")
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
