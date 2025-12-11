# webapp/admin.py
from django.contrib import admin
from .models import Article, ArticleImage, Keyword, ArticleKeyword

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1

class ArticleKeywordInline(admin.TabularInline):
    model = ArticleKeyword
    extra = 3

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'date_written']  # Removed date_published and status
    list_filter = ['author_name']  # Removed status and date_published
    search_fields = ['title', 'content', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleImageInline, ArticleKeywordInline]
    # Removed date_hierarchy = 'date_published'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author_name', 'content', 'date_written')
        }),
        # Removed Dates and Settings fieldsets
    )

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']