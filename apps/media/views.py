from typing import Type, List
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
PHOTOS_TAGS = ['Photos']
ORDERING = ['-is_cover', '-created_at']
DATE_FORMAT = '%b %d, %Y'
PARTIAL_METHOD = 'PATCH'

class PhotoPagination(PageNumberPagination):
    """Pagination class for photos.
    
    Provides page-based pagination with customizable page size.
    """
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


class PhotoViewSet(ViewSet):
    """ViewSet for managing EventPhoto instances.

    Provides endpoints for listing, creating, retrieving, updating, deleting,
    and managing cover photos for event photos.
    """

    serializer_class: Type[PhotoSerializer] = PhotoSerializer
    permission_classes: List[type] = [IsAuthenticated, IsPhotoUploaderOrOrganizerOrAdmin]
    pagination_class: Type[PhotoPagination] = PhotoPagination
    
    def get_queryset(self) -> QuerySet:
        """
        Get the queryset of photos.
        
        Returns:
            QuerySet: All non-deleted photos.
        """
        return EventPhoto.objects.all().select_related('uploaded_by', 'event')
    
    @extend_schema(
        tags=PHOTOS_TAGS,
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
            HTTP_200_OK: OpenApiResponse(
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
        
        event_id = request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(uploaded_by_id=user_id)
        
        queryset = queryset.order_by(*ORDERING)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = PhotoListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PhotoListSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Get photo details',
        description='Returns detailed information about a specific photo.',
        responses={
            HTTP_200_OK: OpenApiResponse(response=PhotoSerializer, description='Photo details'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """
        Retrieve photo details.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Photo details (200) or not found (404).
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=HTTP_200_OK)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Upload new photo',
        description='Upload a new photo to an event. Must be event participant or organizer.',
        request=PhotoCreateSerializer,
        responses={
            HTTP_201_CREATED: OpenApiResponse(response=PhotoSerializer, description='Photo uploaded successfully'),
            HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Not a participant or organizer'),
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
        
        photo = serializer.save(uploaded_by=request.user)
        
        response_serializer = PhotoSerializer(photo)
        return Response(response_serializer.data, status=HTTP_201_CREATED)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Update photo',
        description='Update photo caption and URL. Only the uploader can update.',
        request=PhotoUpdateSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(response=PhotoSerializer, description='Photo updated successfully'),
            HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Permission denied'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    def update(self, request: Request, pk: int) -> Response:
        """
        Update a photo.
        
        Only the photo uploader can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        self.check_object_permissions(request, photo)
        
        partial = request.method == PARTIAL_METHOD
        serializer = PhotoUpdateSerializer(
            photo,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        photo = serializer.save()
        
        response_serializer = PhotoSerializer(photo)
        return Response(response_serializer.data, status=HTTP_200_OK)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Partial update photo',
        description='Partially update photo caption and URL. Only the uploader can update.',
        request=PhotoUpdateSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(response=PhotoSerializer, description='Photo updated successfully'),
            HTTP_400_BAD_REQUEST: OpenApiResponse(description='Invalid input data'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Permission denied'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    def partial_update(self, request: Request, pk: int) -> Response:
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
        tags=PHOTOS_TAGS,
        summary='Delete photo',
        description='Soft delete a photo. Uploader, event organizer, or admin can delete.',
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description='Photo deleted successfully'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Permission denied'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    def destroy(self, request: Request, pk: int) -> Response:
        """
        Delete a photo (soft delete).
        
        Uploader, event organizer, or admin can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: No content (204) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        self.check_object_permissions(request, photo)
        
        photo.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Set as cover photo',
        description='Set this photo as the event cover photo. Only event organizer or admin can do this.',
        responses={
            HTTP_200_OK: OpenApiResponse(response=PhotoSerializer, description='Cover photo set successfully'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Permission denied - not event organizer'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEventOrganizerOrAdmin])
    def set_cover(self, request: Request, pk: int) -> Response:
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
        
        self.check_object_permissions(request, photo)
        
        photo.set_as_cover()
        
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=HTTP_200_OK)
    
    @extend_schema(
        tags=PHOTOS_TAGS,
        summary='Remove cover status',
        description='Remove cover photo status from this photo. Only event organizer or admin can do this.',
        responses={
            HTTP_200_OK: OpenApiResponse(response=PhotoSerializer, description='Cover status removed successfully'),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Authentication required'),
            HTTP_403_FORBIDDEN: OpenApiResponse(description='Permission denied - not event organizer'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Photo not found'),
        },
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEventOrganizerOrAdmin])
    def remove_cover(self, request: Request, pk: int) -> Response:
        """
        Remove cover status from photo.
        
        Only event organizer or admin can perform this action.
        
        Args:
            pk: Photo ID.
        
        Returns:
            Response: Updated photo data (200) or errors.
        """
        photo = get_object_or_404(self.get_queryset(), pk=pk)
        
        self.check_object_permissions(request, photo)
        
        photo.remove_as_cover()
        
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=HTTP_200_OK)

