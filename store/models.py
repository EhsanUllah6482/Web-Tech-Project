from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    original_price = models.IntegerField(blank=True, null=True)  # To store the original price
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    is_black_friday_sale = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save the original price before applying discount
        if self.is_black_friday_sale and not self.original_price:
            self.original_price = self.price
            self.price = int(self.price * 0.6)  # Apply 40% discount
        elif not self.is_black_friday_sale and self.original_price:
            self.price = self.original_price  # Restore original price
            self.original_price = None
        super(Product, self).save(*args, **kwargs)

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


# class Product(models.Model):
#     product_name = models.CharField(max_length=200, unique=True)
#     slug = models.SlugField(max_length=200, unique=True)
#     description = models.TextField(max_length=500, blank=True)
#     price = models.IntegerField()
#     images = models.ImageField(upload_to="photos/products")
#     stock = models.IntegerField()
#     is_available = models.BooleanField(default=True)
#     is_black_friday_sale = models.BooleanField(default=False)  
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     created_date = models.DateTimeField(auto_now_add=True)
#     modified_date = models.DateTimeField(auto_now=True)


#     def get_url(self):
#         return reverse("product_detail", args=[self.category.slug, self.slug])

#     def __str__(self):
#         return self.product_name

#     def averageReview(self):
#         reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
#         avg = 0
#         if reviews['average'] is not None:
#             avg = float(reviews['average'])
#         return avg

#     def discounted_price(self):
#         if self.is_black_friday_sale:
#             return self.price * 0.6  # 40% off
#         return self.price

    
#     def countReview(self):
#         reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
#         count = 0
#         if reviews['count'] is not None:
#             count = int(reviews['count'])
#         return count

from django.conf import settings

class UserInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField(default=0)  # Use a 1-5 rating system
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.product_name}"

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject



class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'
