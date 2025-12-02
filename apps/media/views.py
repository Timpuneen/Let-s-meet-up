"""
ViewSet for managing EventPhoto instances.

This module provides RESTful API endpoints for photo operations
including CRUD operations, filtering, pagination, and cover photo management.
"""

from typing import List, Optional

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import EventPhoto
from .serializers import (
    PhotoSerializer,
    PhotoListSerializer,
    PhotoCreateSerializer,
    PhotoUpdateSerializer,
)
from .permissions import IsPhotoUploaderOrOrganizerOrAdmin, IsEventOrganizerOrAdmin


class PhotoPagination(PageNumberPagination):
    """
    Pagination class for photos.
    
    Provides page-based pagination with customizable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PhotoViewSet(ViewSet):
    """
    ViewSet for managing EventPhoto instances.
    
    Provides endpoints for:
    - Listing photos (with filtering by event and user)
    - Creating photos (participants and organizers only)
    - Retrieving photo details
    - Updating photos (uploader only)
    - Deleting photos (uploader, organizer, or admin)
    - Setting/removing cover photos (organizer or admin)
    """
    
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated, IsPhotoUploaderOrOrganizerOrAdmin]
    pagination_class = PhotoPagination
    
    def get_queryset(self) -> QuerySet:
        """
        Get the queryset of photos.
        
        Returns:
            QuerySet: All non-deleted photos.
        """
        return EventPhoto.objects.all().select_related('uploaded_by', 'event')
    
    @extend_schema(
        tags=['Photos'],
        summary='List all photos',
        description='Returns a paginated list of photos. Can be filtered by event_id and user_id.',
        parameters=[
            OpenApiParameter(
                name='event',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter photos by event ID',
                required=False,
            ),
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter photos by uploader ID',
                required=False,
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page (max 100)',
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=PhotoListSerializer(many=True),
                description='Paginated list of photos'
            ),
        },
    )
    def list(self, request: Request) -> Response:
        """
        List all photos with optional filtering.
        
        Query Parameters:
            event (int): Filter by event ID.
            user (int): Filter by uploader ID.
            page (int): Page number.
            page_size (int): Number of items per page.
        
        Returns:
            Response: Paginated list of photos (200).
        """
        queryset = self.get_queryset()
        
        # Filter by event if provided
        event_id = request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by user if provided
        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(uploaded_by_id=user_id)
        
        # Order by cover status first, then creation date
        queryset = queryset.order_by('-is_cover', '-created_at')
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PhotoListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = PhotoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Photos'],
        summary='Get photo details',
        description='Returns detailed information about a specific photo.',
        responses={
            200: OpenApiResponse(response=PhotoSerializer, description='Photo details'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    def retrieve(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Retrieve photo details.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Photo details (200) or not found (404).
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Photos'],
        summary='Upload new photo',
        description='Upload a new photo to an event. Must be event participant or organizer.',
        request=PhotoCreateSerializer,
        responses={
            201: OpenApiResponse(response=PhotoSerializer, description='Photo uploaded successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Not a participant or organizer'),
        },
    )
    def create(self, request: Request) -> Response:
        """
        Upload a new photo.
        
        The authenticated user is automatically set as the uploader.
        User must be a participant or organizer of the event.
        
        Returns:
            Response: Created photo data (201) or validation errors (400).
        """
        serializer = PhotoCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Set the uploader from the request
        photo = serializer.save(uploaded_by=request.user)
        
        # Return full photo data
        response_serializer = PhotoSerializer(photo)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        tags=['Photos'],
        summary='Update photo',
        description='Update photo caption and URL. Only the uploader can update.',
        request=PhotoUpdateSerializer,
        responses={
            200: OpenApiResponse(response=PhotoSerializer, description='Photo updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    def update(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Update a photo.
        
        Only the photo uploader can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, photo)
        
        partial = request.method == 'PATCH'
        serializer = PhotoUpdateSerializer(
            photo,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        photo = serializer.save()
        
        # Return full photo data
        response_serializer = PhotoSerializer(photo)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Photos'],
        summary='Partial update photo',
        description='Partially update photo caption and URL. Only the uploader can update.',
        request=PhotoUpdateSerializer,
        responses={
            200: OpenApiResponse(response=PhotoSerializer, description='Photo updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    def partial_update(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Partially update a photo.
        
        Only the photo uploader can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        return self.update(request, pk=pk)
    
    @extend_schema(
        tags=['Photos'],
        summary='Delete photo',
        description='Soft delete a photo. Uploader, event organizer, or admin can delete.',
        responses={
            204: OpenApiResponse(description='Photo deleted successfully'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    def destroy(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Delete a photo (soft delete).
        
        Uploader, event organizer, or admin can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: No content (204) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, photo)
        
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['Photos'],
        summary='Set as cover photo',
        description='Set this photo as the event cover photo. Only event organizer or admin can do this.',
        responses={
            200: OpenApiResponse(response=PhotoSerializer, description='Cover photo set successfully'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied - not event organizer'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEventOrganizerOrAdmin])
    def set_cover(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Set photo as event cover.
        
        Only event organizer or admin can perform this action.
        Automatically removes cover status from other photos.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, photo)
        
        # Set as cover (automatically removes cover from others)
        photo.set_as_cover()
        
        # Return updated photo data
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Photos'],
        summary='Remove cover status',
        description='Remove cover photo status from this photo. Only event organizer or admin can do this.',
        responses={
            200: OpenApiResponse(response=PhotoSerializer, description='Cover status removed successfully'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied - not event organizer'),
            404: OpenApiResponse(description='Photo not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEventOrganizerOrAdmin])
    def remove_cover(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Remove cover status from photo.
        
        Only event organizer or admin can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, photo)
        
        # Remove cover status
        photo.remove_as_cover()
        
        # Return updated photo data
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_200_OK)

