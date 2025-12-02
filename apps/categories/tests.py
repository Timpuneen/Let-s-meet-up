import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from .models import Category


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture for regular authenticated user."""
    return User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        name='Test User'
    )


@pytest.fixture
def admin_user(db):
    """Fixture for admin user."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        name='Admin User'
    )


@pytest.fixture
def category(db):
    """Fixture for a test category."""
    return Category.objects.create(
        name='Technology',
        slug='technology'
    )


@pytest.fixture
def categories(db):
    """Fixture for multiple test categories."""
    return [
        Category.objects.create(
            name='Technology',
            slug='technology'
        ),
        Category.objects.create(
            name='Sports',
            slug='sports'
        ),
        Category.objects.create(
            name='Music',
            slug='music'
        ),
    ]


@pytest.mark.django_db
class TestCategoryListView:
    """Tests for listing categories (GET /api/categories/)."""

    def test_list_categories_success(self, api_client, categories):
        """Test successful retrieval of category list."""
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]['name'] == 'Music'
        assert 'slug' in response.data[0]

    def test_list_categories_empty(self, api_client):
        """Test listing when no categories exist."""
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_categories_authenticated(self, api_client, user, categories):
        """Test that authenticated users can also list categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


@pytest.mark.django_db
class TestCategoryRetrieveView:
    """Tests for retrieving category details (GET /api/categories/{id}/)."""

    def test_retrieve_category_success(self, api_client, category):
        """Test successful retrieval of category details."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert response.data['name'] == 'Technology'
        assert response.data['slug'] == 'technology'

    def test_retrieve_category_not_found(self, api_client):
        """Test retrieving a non-existent category."""
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_authenticated(self, api_client, user, category):
        """Test that authenticated users can retrieve category details."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id


@pytest.mark.django_db
class TestCategoryCreateView:
    """Tests for creating categories (POST /api/categories/)."""

    def test_create_category_success(self, api_client, admin_user):
        """Test successful category creation by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Category'
        assert response.data['slug'] == 'new-category'
        assert Category.objects.filter(slug='new-category').exists()

    def test_create_category_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create categories."""
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_regular_user_forbidden(self, api_client, user):
        """Test that regular users cannot create categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_category_missing_name(self, api_client, admin_user):
        """Test creating category without required name field."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'slug': 'test-slug'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_create_category_missing_slug(self, api_client, admin_user):
        """Test creating category without required slug field."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'Test Category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data

    def test_create_category_duplicate_slug(self, api_client, admin_user, category):
        """Test creating category with duplicate slug."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'Another Tech',
            'slug': 'technology'  
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data


@pytest.mark.django_db
class TestCategoryUpdateView:
    """Tests for updating categories (PUT/PATCH /api/categories/{id}/)."""

    def test_update_category_success(self, api_client, admin_user, category):
        """Test successful category update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Updated Technology',
            'slug': 'updated-technology'
        }
        response = api_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Technology'
        assert response.data['slug'] == 'updated-technology'
        
        category.refresh_from_db()
        assert category.name == 'Updated Technology'
        assert category.slug == 'updated-technology'

    def test_partial_update_category_success(self, api_client, admin_user, category):
        """Test successful partial category update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Partially Updated'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Partially Updated'
        assert response.data['slug'] == 'technology'  
        
        category.refresh_from_db()
        assert category.name == 'Partially Updated'
        assert category.slug == 'technology'

    def test_update_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot update categories."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Should Not Update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category_regular_user_forbidden(self, api_client, user, category):
        """Test that regular users cannot update categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Should Not Update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_category_not_found(self, api_client, admin_user):
        """Test updating a non-existent category."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        data = {
            'name': 'Does Not Exist'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_duplicate_slug(self, api_client, admin_user, categories):
        """Test updating category with duplicate slug."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': categories[0].pk})
        data = {
            'slug': 'sports' 
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryDeleteView:
    """Tests for deleting categories (DELETE /api/categories/{id}/)."""

    def test_delete_category_success(self, api_client, admin_user, category):
        """Test successful category deletion by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot delete categories."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_regular_user_forbidden(self, api_client, user, category):
        """Test that regular users cannot delete categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_not_found(self, api_client, admin_user):
        """Test deleting a non-existent category."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryPermissions:
    """Comprehensive tests for category permissions."""

    def test_anonymous_can_read_only(self, api_client, category):
        """Test that anonymous users have read-only access."""
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(list_url, {'name': 'Test', 'slug': 'test'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.patch(detail_url, {'name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_can_read_only(self, api_client, user, category):
        """Test that regular authenticated users have read-only access."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(list_url, {'name': 'Test', 'slug': 'test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.patch(detail_url, {'name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_has_full_access(self, api_client, admin_user, category):
        """Test that admin users have full CRUD access."""
        api_client.force_authenticate(user=admin_user)
        
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'name': 'Admin Category', 'slug': 'admin-category'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = api_client.patch(
            detail_url,
            {'name': 'Updated by Admin'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT