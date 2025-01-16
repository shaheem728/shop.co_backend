from django.db import models
from django.contrib.auth.models import User
import uuid

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Style(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name               

class Color(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name      

class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name                 

class Products(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(null=True, blank=True, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE, null=True, blank=True)
    sizes = models.ManyToManyField(Size,blank=True)
    rating = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="colors")
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.product.name} - {self.color.name}"

class ProductImages(models.Model):
    product_color = models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        related_name='images',  # This is the key for reverse relationship
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='products_image/', null=True, blank=True)

    def __str__(self):
        return f"{self.product_color.color.name}-{self.product_color.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_review')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    rating = models.IntegerField(null=True, blank=True, default=0)
    comment = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return (f"{self.product.name}-{self.rating}")