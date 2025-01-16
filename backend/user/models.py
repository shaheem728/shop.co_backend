from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from product.models import Products
from django.utils.timezone import now
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')    
    mobile = models.CharField(max_length=15,null=True,unique=True) 
    address = models.TextField(null=True)
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created and not hasattr(instance, 'profile'):  # Prevent overriding existing profile
            Profile.objects.create(user=instance)

    def __str__(self):
      return f'{self.user}\n{self.mobile}\n{self.user.id}'
      
class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tokens for {self.user.username}"      

class Order(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    paymentMethod = models.CharField(max_length=200, null=True, blank=True)
    totalPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(auto_now_add=False,null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Order by {self.user.username}"

class OrderItem(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    image = models.CharField(max_length=200, null=True, blank=True)
    color =models.CharField(max_length=50, null=True, blank=True)
    size =models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

class ShippingAddress(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping_address')
    country = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    postalCode = models.CharField(max_length=20, null=True, blank=True)  # Removed extra "."
    
    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


