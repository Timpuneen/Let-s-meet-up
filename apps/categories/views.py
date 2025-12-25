from typing import List, Optional, Type

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.request import Request

from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Category
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer
)


ACTION_LIST: str = 'list'
ACTION_RETRIEVE: str = 'retrieve'


class CategoryViewSet(ViewSet):
    """
    ViewSet for managing Category instances.

    Provides endpoints for:
    - Listing categories (public)
    - Retrieving category details (public)
    - Creating categories (admin only)
    - Updating categories (admin only)
    - Deleting categories (admin only)
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self) -> List[BasePermission]:
        """
        Instantiate and return the list of permissions that this view requires.
        
        Public actions (list, retrieve) allow any access.
        All other actions require authentication and admin privileges.
        
        Returns:
            List[BasePermission]: Permission instances based on the action.
        """
        if self.action in [ACTION_LIST, ACTION_RETRIEVE]:
            permission_classes: List[Type[BasePermission]] = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self) -> QuerySet:
        """
        Get the queryset of categories.
        
        Returns:
            QuerySet: All categories ordered by name.
        """
        return Category.objects.all()

    @extend_schema(
        tags=['Categories'],
        summary='List all categories',
        description='Returns a list of all available categories.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CategoryListSerializer(many=True),
                description='List of categories'
            ),
        },
    )
    def list(self, request: Request) -> Response:
        """
        List all categories.
        
        Args:
            request: The HTTP request object.
        
        Returns:
            Response: List of categories with HTTP 200 status.
        """
        queryset = self.get_queryset()
        serializer = CategoryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        summary='Get category details',
        description='Returns detailed information about a specific category.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CategorySerializer,
                description='Category details'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Category not found'
            ),
        },
    )
    def retrieve(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Retrieve category details.
        
        Args:
            request: The HTTP request object.
            pk: Category ID.
        
        Returns:
            Response: Category details with HTTP 200 status or HTTP 404 if not found.
        """
        category: Category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Categories'],
        summary='Create new category',
        description='Create a new category. Admin authentication required.',
        request=CategoryCreateSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=CategorySerializer,
                description='Category created successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Admin privileges required'
            ),
        },
    )
    def create(self, request: Request) -> Response:
        """
        Create a new category.
        
        Args:
            request: The HTTP request object containing category data.
        
        Returns:
            Response: Created category data with HTTP 201 status or validation errors with HTTP 400 status.
        """
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category: Category = serializer.save()
        
        response_serializer = CategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def _update_category(self, request: Request, pk: Optional[int], partial: bool) -> Response:
        """
        Internal method to handle category updates.
        
        Args:
            request: The HTTP request object containing updated data.
            pk: Category ID.
            partial: Whether this is a partial update (PATCH) or full update (PUT).
        
        Returns:
            Response: Updated category data with HTTP 200 status or appropriate error response.
        """
        category: Category = get_object_or_404(self.get_queryset(), pk=pk)
        
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
        summary='Update category',
        description='Full update of category fields (PUT). Admin authentication required.',
        request=CategoryUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CategorySerializer,
                description='Category updated successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Admin privileges required'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Category not found'
            ),
        },
    )
    def update(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Full update of a category (PUT).
        
        Args:
            request: The HTTP request object containing updated data.
            pk: Category ID.
        
        Returns:
            Response: Updated category data with HTTP 200 status or appropriate error response.
        """
        return self._update_category(request, pk, partial=False)

    @extend_schema(
        tags=['Categories'],
        summary='Partial update category',
        description='Partial update of category fields (PATCH). Admin authentication required.',
        request=CategoryUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CategorySerializer,
                description='Category updated successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Admin privileges required'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Category not found'
            ),
        },
    )
    def partial_update(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Partial update of a category (PATCH).
        
        Args:
            request: The HTTP request object containing partial update data.
            pk: Category ID.
        
        Returns:
            Response: Updated category data with HTTP 200 status or appropriate error response.
        """
        return self._update_category(request, pk, partial=True)

    @extend_schema(
        tags=['Categories'],
        summary='Delete category',
        description='Delete a category. Admin authentication required.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='Category deleted successfully'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Admin privileges required'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Category not found'
            ),
        },
    )
    def destroy(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Delete a category.
        
        Args:
            request: The HTTP request object.
            pk: Category ID.
        
        Returns:
            Response: HTTP 204 No Content status on success or appropriate error response.
        """
        category: Category = get_object_or_404(self.get_queryset(), pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)