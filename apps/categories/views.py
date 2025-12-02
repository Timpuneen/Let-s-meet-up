from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Category
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer
)


class CategoryViewSet(ViewSet):
    """
    ViewSet for managing Category instances.

    Provides endpoints for:
    - Listing categories
    - Creating categories
    - Retrieving category details
    - Updating categories (admin only)
    - Deleting categories (admin only)
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        
        Returns:
            list: Permission instances based on the action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=['Categories'],
        summary='List all categories',
        description='Returns a list of all available categories.',
        responses={
            200: OpenApiResponse(response=CategoryListSerializer(many=True), description='List of categories'),
        },
    )
    def list(self, request):
        """
        List all categories.
        
        Returns:
            Response: List of categories (200).
        """
        queryset = Category.objects.all()
        serializer = CategoryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        summary='Get category details',
        description='Returns detailed information about a specific category.',
        responses={
            200: OpenApiResponse(response=CategorySerializer, description='Category details'),
            404: OpenApiResponse(description='Category not found'),
        },
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve category details.
        
        Args:
            pk: Category ID.
        
        Returns:
            Response: Category details (200) or not found (404).
        """
        category = get_object_or_404(Category.objects.all(), pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        summary='Create new category',
        description='Create a new category. Authentication required.',
        request=CategoryCreateSerializer,
        responses={
            201: OpenApiResponse(response=CategorySerializer, description='Category created successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    def create(self, request):
        """
        Create a new category.
        
        Returns:
            Response: Created category data (201) or validation errors (400).
        """
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        
        response_serializer = CategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Categories'],
        summary='Update category',
        description='Update category fields. Authentication required.',
        request=CategoryUpdateSerializer,
        responses={
            200: OpenApiResponse(response=CategorySerializer, description='Category updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='Category not found'),
        },
    )
    def update(self, request, pk=None):
        """
        Update a category.
        
        Args:
            pk: Category ID.
        
        Returns:
            Response: Updated category data (200) or errors.
        """
        category = get_object_or_404(Category.objects.all(), pk=pk)
        
        partial = request.method == 'PATCH'
        serializer = CategoryUpdateSerializer(
            category,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        
        response_serializer = CategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        summary='Partial update category',
        description='Partially update category fields. Authentication required.',
        request=CategoryUpdateSerializer,
        responses={
            200: OpenApiResponse(response=CategorySerializer, description='Category updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='Category not found'),
        },
    )
    def partial_update(self, request, pk=None):
        """
        Partially update a category.
        
        Args:
            pk: Category ID.
        
        Returns:
            Response: Updated category data (200) or errors.
        """
        return self.update(request, pk=pk)

    @extend_schema(
        tags=['Categories'],
        summary='Delete category',
        description='Delete a category. Authentication required.',
        responses={
            204: OpenApiResponse(description='Category deleted successfully'),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='Category not found'),
        },
    )
    def destroy(self, request, pk=None):
        """
        Delete a category.
        
        Args:
            pk: Category ID.
        
        Returns:
            Response: No content (204) or errors.
        """
        category = get_object_or_404(Category.objects.all(), pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
