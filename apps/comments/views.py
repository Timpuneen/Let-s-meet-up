"""
ViewSet for managing EventComment instances.

This module provides RESTful API endpoints for comment operations
including CRUD operations, filtering, pagination, and nested replies.
"""

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import EventComment
from .serializers import (
    CommentSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    NestedReplySerializer,
)
from .permissions import IsCommentOwnerOrAdminOrReadOnly


class CommentPagination(PageNumberPagination):
    """
    Pagination class for comments.
    
    Provides page-based pagination with customizable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentViewSet(ViewSet):
    """
    ViewSet for managing EventComment instances.
    
    Provides endpoints for:
    - Listing comments (with filtering by event and user)
    - Creating comments
    - Retrieving comment details
    - Updating comments (owner or admin only)
    - Deleting comments (owner or admin only)
    - Retrieving nested replies
    """
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentOwnerOrAdminOrReadOnly]
    pagination_class = CommentPagination
    
    def get_queryset(self):
        """
        Get the queryset of comments.
        
        Returns:
            QuerySet: All non-deleted comments.
        """
        return EventComment.objects.all().select_related('user', 'event', 'parent')
    
    @extend_schema(
        tags=['Comments'],
        summary='List all comments',
        description='Returns a paginated list of comments. Can be filtered by event_id and user_id.',
        parameters=[
            OpenApiParameter(
                name='event',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter comments by event ID',
                required=False,
            ),
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter comments by user ID',
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
                response=CommentListSerializer(many=True),
                description='Paginated list of comments'
            ),
        },
    )
    def list(self, request):
        """
        List all comments with optional filtering.
        
        Query Parameters:
            event (int): Filter by event ID.
            user (int): Filter by user ID.
            page (int): Page number.
            page_size (int): Number of items per page.
        
        Returns:
            Response: Paginated list of comments (200).
        """
        queryset = self.get_queryset()
        
        # Filter by event if provided
        event_id = request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by user if provided
        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Order by creation date
        queryset = queryset.order_by('created_at')
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = CommentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = CommentListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Comments'],
        summary='Get comment details',
        description='Returns detailed information about a specific comment.',
        responses={
            200: OpenApiResponse(response=CommentSerializer, description='Comment details'),
            404: OpenApiResponse(description='Comment not found'),
        },
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve comment details.
        
        Args:
            pk: Comment ID.
        
        Returns:
            Response: Comment details (200) or not found (404).
        """
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Comments'],
        summary='Create new comment',
        description='Create a new comment on an event. The authenticated user is automatically set as the comment author.',
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(response=CommentSerializer, description='Comment created successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    def create(self, request):
        """
        Create a new comment.
        
        The authenticated user is automatically set as the comment author.
        
        Returns:
            Response: Created comment data (201) or validation errors (400).
        """
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the user from the request
        comment = serializer.save(user=request.user)
        
        # Return full comment data
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        tags=['Comments'],
        summary='Update comment',
        description='Update comment content. Only the comment owner or admin can update.',
        request=CommentUpdateSerializer,
        responses={
            200: OpenApiResponse(response=CommentSerializer, description='Comment updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Comment not found'),
        },
    )
    def update(self, request, pk=None):
        """
        Update a comment.
        
        Only the comment owner or admin can perform this action.
        
        Args:
            pk: Comment ID.
        
        Returns:
            Response: Updated comment data (200) or errors.
        """
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, comment)
        
        partial = request.method == 'PATCH'
        serializer = CommentUpdateSerializer(
            comment,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        # Return full comment data
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Comments'],
        summary='Partial update comment',
        description='Partially update comment content. Only the comment owner or admin can update.',
        request=CommentUpdateSerializer,
        responses={
            200: OpenApiResponse(response=CommentSerializer, description='Comment updated successfully'),
            400: OpenApiResponse(description='Invalid input data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Comment not found'),
        },
    )
    def partial_update(self, request, pk=None):
        """
        Partially update a comment.
        
        Only the comment owner or admin can perform this action.
        
        Args:
            pk: Comment ID.
        
        Returns:
            Response: Updated comment data (200) or errors.
        """
        return self.update(request, pk=pk)
    
    @extend_schema(
        tags=['Comments'],
        summary='Delete comment',
        description='Soft delete a comment. Only the comment owner or admin can delete.',
        responses={
            204: OpenApiResponse(description='Comment deleted successfully'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Comment not found'),
        },
    )
    def destroy(self, request, pk=None):
        """
        Delete a comment (soft delete).
        
        Only the comment owner or admin can perform this action.
        
        Args:
            pk: Comment ID.
        
        Returns:
            Response: No content (204) or errors.
        """
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check object-level permissions
        self.check_object_permissions(request, comment)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['Comments'],
        summary='Get nested replies',
        description='Returns all nested replies to a specific comment in a tree structure.',
        responses={
            200: OpenApiResponse(
                response=NestedReplySerializer(many=True),
                description='Nested replies tree'
            ),
            404: OpenApiResponse(description='Comment not found'),
        },
    )
    @action(detail=True, methods=['get'], url_path='replies')
    def replies(self, request, pk=None):
        """
        Get all nested replies to a comment.
        
        Returns replies in a tree structure with all nested levels.
        
        Args:
            pk: Comment ID.
        
        Returns:
            Response: Nested replies tree (200) or not found (404).
        """
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Get direct replies
        replies = comment.replies.all().order_by('created_at')
        serializer = NestedReplySerializer(replies, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

