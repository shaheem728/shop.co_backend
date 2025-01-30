# serializers.py
from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from product.models import Products
class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ['mobile', 'address','order_mobile']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = False
        self.fields['address'].allow_blank = True
        self.fields['order_mobile'].required = False
        self.fields['order_mobile'].allow_blank = True
    def validate_mobile(self, value):
        """
        Skip validation if the mobile number hasn't changed.
        """
        # Check if the current instance's mobile matches the new value
        if self.instance and self.instance.mobile == value:
            return value  # No change, skip validation

        # Validate uniqueness only if the value is new or changed
        if models.Profile.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("A profile with this mobile already exists.")
        return value
class UserSerializers(serializers.ModelSerializer):
    profile = ProfileSerializers()  # Use the nested serializer
    password = serializers.CharField(write_only=True, required=False)  # Hide password in the response

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'profile']  

    def create(self, validated_data):
        # Extract profile and password data
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        # Create User instance
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Handle Profile creation or update
        if profile_data:
            profile, created = models.Profile.objects.get_or_create(
                user=user,  # Look for existing Profile by User
                defaults={'mobile': profile_data.get('mobile'),
                          'address':profile_data.get('address'),
                          'order_mobile':profile_data.get('order_mobile')},  
            )
            if not created:  # If Profile already exists, update it
                profile.mobile = profile_data.get('mobile')
                profile.address = profile_data.get('address')
                profile.order_mobile = profile_data.get('order_mobile')
                profile.save()
        return user  
class UserProfileSerializers(serializers.ModelSerializer): 
    class Meta:
        model = models.Profile
        fields = ['address', 'order_mobile']
class UserDetailSerializers(serializers.ModelSerializer):
    profile = UserProfileSerializers()
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile'] 
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update the profile fields if provided
        if profile_data:
            profile, _ = models.Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance     
class UserLoginSerializers(serializers.Serializer):
      username = serializers.CharField()
      password = serializers.CharField()
class UserMobileSerializers(serializers.Serializer):
      mobile = serializers.CharField()
class MobileOTPSerializers(serializers.Serializer):
      otp = serializers.CharField()
class ChangePasswordSerializers(serializers.Serializer):
      password = serializers.CharField()
      mobile = serializers.CharField()
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField()
    class Meta:
        model = models.OrderItem
        fields = ['product_id','order','product','name','quantity','price','image', 'color','size']
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShippingAddress
        fields = '__all__'
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=True)  
    shipping_address = ShippingAddressSerializer(required=True) 
    user = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Order
        fields = [
            'uuid', 'user', 'paymentMethod', 'totalPrice', 'createdAt',
            'order_items', 'shipping_address'
        ]
    def get_user(self, obj):
        # Return the user information associated with the order
        return {
            'id': obj.user.id,
        }
    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        shipping_address_data = validated_data.pop('shipping_address')
        order = models.Order.objects.create(**validated_data)      
        # Create OrderItems
        for item_data in order_items_data:
            product_id = item_data.pop('product_id', None)  
            product = models.Products.objects.get(id=product_id)
            models.OrderItem.objects.create(order=order, product=product, **item_data)
        # Create ShippingAddress
        models.ShippingAddress.objects.create(order=order, **shipping_address_data)
        return order     
class orderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=True)  
    user = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Order
        fields = [
            'uuid', 'user', 'totalPrice', 'isDelivered', 'deliveredAt', 'order_items','createdAt','isPaid','paidAt'
        ]
    def get_user(self, obj):
        # Return the user information associated with the order
        return {
            'id': obj.user.id,
        }