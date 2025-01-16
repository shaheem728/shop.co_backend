from . import models
from rest_framework import serializers

from rest_framework import serializers


 
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=models.Products.objects.all(), read_only=False)

    class Meta:
        model = models.Review
        fields = ['product', 'user', 'rating', 'comment', 'createdAt']

    def get_user(self, obj):
        if obj.user:  
            return {
                'id': obj.user.id,
                'username': obj.user.username,
            }
        return None  # Return None if the user is not set

    def create(self, validated_data):
        # Get the currently authenticated user from the request context
        user = self.context['request'].user

        # Extract the product ID from validated_data
        product = validated_data.pop('product')

        # Create the review instance with the authenticated user
        review = models.Review.objects.create(user=user, product=product, **validated_data)

        return review
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImages
        fields = ['image']  # Include only the image field

# Serializer for product colors
class ProductColorSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(source='color.name', read_only=True)  # Retrieve the color name
    images = ProductImageSerializer(many=True, read_only=True)  # Include related images

    class Meta:
        model = models.ProductColor
        fields = ['color_name', 'images']  # Add the fields you want to expose

# Serializer for products
class ProductsSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)  # Retrieve category name
    style = serializers.CharField(source='style.name', read_only=True)  # Retrieve style name
    colors = ProductColorSerializer(many=True, read_only=True)  # Include colors with images
    sizes = serializers.SerializerMethodField()  # Retrieve sizes as a list of names

    class Meta:
        model = models.Products
        fields = [
            'id', 'uuid', 'name', 'description', 'price', 'stock', 'rating',
            'category', 'style', 'sizes', 'discount', 'colors'
        ]

    def get_sizes(self, obj):
        """Retrieve all sizes associated with the product."""
        return [size.name for size in obj.sizes.all()]  # Return size names as a lis
      
