from typing import Optional

from rest_framework import status
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

from .models import EventComment
from .serializers import (
    CommentSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    NestedReplySerializer,
)
from .permissions import IsCommentOwnerOrAdminOrReadOnly


DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100


class CommentPagination(PageNumberPagination):
    """
    Pagination class for comments.
    
    Provides page-based pagination with customizable page size.
    """
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


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
    
    def get_queryset(self) -> QuerySet[EventComment]:
        """
        Get the queryset of comments.
        
        Returns:
            QuerySet: All non-deleted comments with related user, event, and parent objects.
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
            status.HTTP_200_OK: OpenApiResponse(
                response=CommentListSerializer(many=True),
                description='Paginated list of comments'
            ),
        },
    )
    def list(self, request: Request) -> Response:
        """
        List all comments with optional filtering.
        
        Query Parameters:
            event (int): Filter by event ID.
            user (int): Filter by user ID.
            page (int): Page number.
            page_size (int): Number of items per page.
        
        Returns:
            Response: Paginated list of comments with HTTP 200 status.
        """
        queryset = self.get_queryset()
        
        event_id: Optional[str] = request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        user_id: Optional[str] = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('created_at')
        
        paginator: CommentPagination = self.pagination_class()
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
            status.HTTP_200_OK: OpenApiResponse(
                response=CommentSerializer,
                description='Comment details'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Comment not found'
            ),
        },
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """
        Retrieve comment details.
        
        Args:
            request: The HTTP request object.
            pk: Comment ID.
        
        Returns:
            Response: Comment details with HTTP 200 status or HTTP 404 if not found.
        """
        comment: EventComment = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Comments'],
        summary='Create new comment',
        description='Create a new comment on an event. The authenticated user is automatically set as the comment author.',
        request=CommentCreateSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=CommentSerializer,
                description='Comment created successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
        },
    )
    def create(self, request: Request) -> Response:
        """
        Create a new comment.
        
        The authenticated user is automatically set as the comment author.
        
        Args:
            request: The HTTP request object containing comment data.
        
        Returns:
            Response: Created comment data with HTTP 201 status or validation errors with HTTP 400 status.
        """
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment: EventComment = serializer.save(user=request.user)
        
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        tags=['Comments'],
        summary='Update comment',
        description='Update comment content. Only the comment owner or admin can update.',
        request=CommentUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CommentSerializer,
                description='Comment updated successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Permission denied'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Comment not found'
            ),
        },
    )
    def update(self, request: Request, pk: int) -> Response:
        """
        Update a comment.
        
        Only the comment owner or admin can perform this action.
        
        Args:
            request: The HTTP request object containing updated data.
            pk: Comment ID.
        
        Returns:
            Response: Updated comment data with HTTP 200 status or appropriate error response.
        """
        comment: EventComment = get_object_or_404(self.get_queryset(), pk=pk)
        
        self.check_object_permissions(request, comment)
        
        partial: bool = request.method == 'PATCH'
        serializer = CommentUpdateSerializer(
            comment,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Comments'],
        summary='Partial update comment',
        description='Partially update comment content. Only the comment owner or admin can update.',
        request=CommentUpdateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CommentSerializer,
                description='Comment updated successfully'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid input data'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Permission denied'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Comment not found'
            ),
        },
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        """
        Partially update a comment.
        
        Only the comment owner or admin can perform this action.
        
        Args:
            request: The HTTP request object containing partial update data.
            pk: Comment ID.
        
        Returns:
            Response: Updated comment data with HTTP 200 status or appropriate error response.
        """
        return self.update(request, pk=pk)
    
    @extend_schema(
        tags=['Comments'],
        summary='Delete comment',
        description='Soft delete a comment. Only the comment owner or admin can delete.',
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description='Comment deleted successfully'
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description='Authentication required'
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Permission denied'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Comment not found'
            ),
        },
    )
    def destroy(self, request: Request, pk: int) -> Response:
        """
        Delete a comment (soft delete).
        
        Only the comment owner or admin can perform this action.
        
        Args:
            request: The HTTP request object.
            pk: Comment ID.
        
        Returns:
            Response: HTTP 204 No Content status on success or appropriate error response.
        """
        comment: EventComment = get_object_or_404(self.get_queryset(), pk=pk)
        
        self.check_object_permissions(request, comment)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['Comments'],
        summary='Get nested replies',
        description='Returns all nested replies to a specific comment in a tree structure.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=NestedReplySerializer(many=True),
                description='Nested replies tree'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Comment not found'
            ),
        },
    )
    @action(detail=True, methods=['get'], url_path='replies')
    def replies(self, request: Request, pk: int) -> Response:
        """
        Get all nested replies to a comment.
        
        Returns replies in a tree structure with all nested levels.
        
        Args:
            request: The HTTP request object.
            pk: Comment ID.
        
        Returns:
            Response: Nested replies tree with HTTP 200 status or HTTP 404 if comment not found.
        """
        comment: EventComment = get_object_or_404(self.get_queryset(), pk=pk)
        
        replies: QuerySet[EventComment] = comment.replies.all().order_by('created_at')
        serializer = NestedReplySerializer(replies, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)