from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer


class SignupView(APIView):
    """
    Register a new user account.
    
    Creates a new user account and returns the user data along with JWT tokens.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Authentication'],
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description='User successfully created'
            ),
            400: OpenApiResponse(description='Invalid input data')
        },
        summary='Register new user',
        description='Create a new user account with email, name, and password. Returns user data and JWT tokens.',
    )
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Authenticate user and get JWT tokens.
    
    Validates user credentials and returns JWT access and refresh tokens.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Authentication'],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='Successfully authenticated'
            ),
            400: OpenApiResponse(description='Invalid credentials')
        },
        summary='User login',
        description='Authenticate with email and password. Returns user data and JWT tokens.',
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveAPIView):
    """
    Get current authenticated user information.
    
    Returns the profile information of the currently logged-in user.
    Requires authentication via JWT token.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    @extend_schema(
        tags=['Authentication'],
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='Current user information'
            ),
            401: OpenApiResponse(description='Not authenticated')
        },
        summary='Get current user',
        description='Retrieve the profile of the currently authenticated user.',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user
