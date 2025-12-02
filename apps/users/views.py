from typing import List, Any

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    AuthTokenSerializer,
)


class AuthViewSet(ViewSet):
    """
    ViewSet for user authentication operations.

    Provides endpoints for user registration, login, and profile retrieval.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self) -> List[BasePermission]:
        """
        Instantiate and return the list of permissions that this view requires.

        Returns:
            list: Permission classes based on the action.
        """
        if self.action in ["signup", "login"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Authentication"],
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=AuthTokenSerializer,
                description="User successfully created with JWT tokens",
            ),
            400: OpenApiResponse(description="Invalid input data"),
        },
        summary="Register new user",
        description="Create a new user account with email, name, and password. Returns user data and JWT tokens.",
    )
    @action(detail=False, methods=["post"])
    def signup(self, request: Request) -> Response:
        """
        Register a new user account.

        Creates a new user account and returns the user data along with JWT tokens.

        Args:
            request: HTTP request containing user registration data.

        Returns:
            Response: User data and JWT tokens (201) or validation errors (400).
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate response with tokens
        response_data = {"user": user}
        token_serializer = AuthTokenSerializer(response_data)

        return Response(token_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=AuthTokenSerializer,
                description="Successfully authenticated with JWT tokens",
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        summary="User login",
        description="Authenticate with email and password. Returns user data and JWT tokens.",
    )
    @action(detail=False, methods=["post"])
    def login(self, request: Request) -> Response:
        """
        Authenticate user and get JWT tokens.

        Validates user credentials and returns JWT access and refresh tokens.

        Args:
            request: HTTP request containing login credentials.

        Returns:
            Response: User data and JWT tokens (200) or validation errors (400).
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Generate response with tokens
        response_data = {"user": user}
        token_serializer = AuthTokenSerializer(response_data)

        return Response(token_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                response=UserSerializer, description="Current user information"
            ),
            401: OpenApiResponse(description="Not authenticated"),
        },
        summary="Get current user",
        description="Retrieve the profile of the currently authenticated user.",
    )
    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """
        Get current authenticated user information.

        Returns the profile information of the currently logged-in user.
        Requires authentication via JWT token.

        Args:
            request: HTTP request with authentication token.

        Returns:
            Response: Current user data (200) or unauthorized (401).
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with OpenAPI documentation.

    Accepts a refresh token and returns a new access token.
    """

    @extend_schema(
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(description="New access token generated"),
            401: OpenApiResponse(description="Invalid or expired refresh token"),
        },
        summary="Refresh access token",
        description="Generate a new access token using a valid refresh token.",
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)
