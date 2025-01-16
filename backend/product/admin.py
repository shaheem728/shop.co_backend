from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Style, Color, Size, Products, ProductColor, ProductImages,Review

# Inline for product images
class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 1  # Number of empty fields for adding images by default
    show_change_link = True

# Inline for product colors
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    show_change_link = True
    inlines = [ProductImageInline]  # Associate images with each color

# Admin panel for Products
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductColorInline]  # Include colors inline with products
    search_fields = ['name']  # Enable search by product name
    list_display = ('name', 'category', 'price', 'stock', 'get_colors', 'get_sizes', 'first_image')
    list_filter = ('category', 'sizes','style')  
    filter_horizontal = ('sizes',)  
    def get_colors(self, obj):
        """Display available colors for the product."""
        return ", ".join([color.color.name for color in obj.colors.all()])
    get_colors.short_description = "Available Colors"

    def get_sizes(self, obj):
        """Display available sizes for the product."""
        return ", ".join([size.name for size in obj.sizes.all()])

    get_sizes.short_description = "Available Sizes"

    def first_image(self, obj):
        """Display the first image of the product."""
        first_color = obj.colors.first()  # Get the first color
        if first_color and first_color.images.first():
            return mark_safe('<img src="%s" width="50">' % first_color.images.first().image.url)
        return "No Image"

    first_image.short_description = "Image Preview"

# Register models in admin
admin.site.register(Category)
admin.site.register(Style)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(ProductImages)  
admin.site.register(ProductColor)  
admin.site.register(Products, ProductTypeAdmin)
admin.site.register(Review)
