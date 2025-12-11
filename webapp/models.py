# webapp/models.py
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

class Article(models.Model):
    # Only essential fields - no defaults needed
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author_name = models.CharField(max_length=100)
    content = models.TextField()
    date_written = models.DateField()
    
    # KEYWORDS RELATIONSHIP
    keywords = models.ManyToManyField('Keyword', through='ArticleKeyword', related_name='articles')
    
    class Meta:
        ordering = ['-date_written']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.article.title}"

class Keyword(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class ArticleKeyword(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_keywords')
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['article', 'keyword']
    
    def __str__(self):
        return f"{self.article.title} - {self.keyword.name}"
    
# Rating System    
class VendorRating(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating from 0 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'user']  # One rating per user per vendor
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.vendor.business_name} - {self.rating} stars"