from rest_framework.serializers import ModelSerializer
from apps.categories.models import Category

class CategorySerializer(ModelSerializer):
    """Serializer for Category model.

    Provides basic category information for read operations.
    Used in nested serializers for events and other resources.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CategoryListSerializer(ModelSerializer):
    """Serializer for listing Category instances.

    Provides a summary view of categories for list endpoints.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CategoryCreateSerializer(ModelSerializer):
    """Serializer for creating and updating Category instances.

    Handles validation and serialization for category creation and updates.
    """

    class Meta:
        model = Category
        fields = ['name', 'slug']

    def create(self, validated_data):
        """Create a new Category instance.

        Args:
            validated_data (dict): Validated data for the new category.

        Returns:
            Category: The created Category instance.
        """
        return Category.objects.create(**validated_data)

class CategoryUpdateSerializer(ModelSerializer):
    """Serializer for updating Category instances.

    Handles partial updates and validation for category updates.
    """

    class Meta:
        model = Category
        fields = ['name', 'slug']

    def update(self, instance, validated_data):
        """Update an existing Category instance.

        Args:
            instance (Category): The Category instance to update.
            validated_data (dict): Validated data for the update.

        Returns:
            Category: The updated Category instance.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance
    
