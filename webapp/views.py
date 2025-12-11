# webapp/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from vendors.models import Vendor, CuisineType, MenuItem, Event  # Import from vendors app
from tours.models import Tour, TourOperator, TourItinerary  # Import Tour models from tours app
from .models import Article, VendorRating, Keyword

def homepage(request):
    """Homepage view"""
    query = request.GET.get('q', '').strip()
    if query:
        # Use urlencode for proper URL encoding
        from django.utils.http import urlencode
        return redirect(reverse('webapp:search') + '?' + urlencode({'q': query}))
    return render(request, 'webapp/homepage.html')

def places_eat(request):
    """Places to Eat main page"""
    # Add your places_eat logic here
    return render(request, 'webapp/places_eat.html')

def restaurants(request):
    # Get filter parameters from request
    selected_cuisines = request.GET.getlist('cuisine')
    selected_locations = request.GET.getlist('location')
    halal_filter = request.GET.get('halal') == 'on'
    kosher_filter = request.GET.get('kosher') == 'on'
    vegetarian_filter = request.GET.get('vegetarian') == 'on'
    
    # Start with all restaurants
    # Make sure this matches your model - if it's Vendor with vendor_type='restaurant'
    restaurants_qs = Vendor.objects.filter(vendor_type='restaurant')  # Adjust based on your model
    
    # Apply filters if they exist
    if selected_cuisines:
        # Adjust field name based on your model
        restaurants_qs = restaurants_qs.filter(cuisine_type__in=selected_cuisines)
    
    if halal_filter:
        restaurants_qs = restaurants_qs.filter(halal=True)
    
    if kosher_filter:
        restaurants_qs = restaurants_qs.filter(kosher=True)
    
    if vegetarian_filter:
        restaurants_qs = restaurants_qs.filter(vegetarian=True)
    
    if selected_locations:
        # Adjust field name based on your model
        restaurants_qs = restaurants_qs.filter(location__in=selected_locations)
    
    # Sort restaurants alphabetically
    restaurants_qs = restaurants_qs.order_by(Lower('business_name'))
    
    # Get all available cuisines for the filter sidebar
    # Adjust based on your model - this might need to be from a different source
    available_cuisines = Vendor.objects.values_list('cuisine_type', flat=True).distinct()
    
    # Get all available locations for the filter sidebar
    available_locations = Vendor.objects.values_list('location', flat=True).distinct()
    
    # Determine which dietary filters to show
    show_halal_filter = Vendor.objects.filter(halal=True).exists()
    show_kosher_filter = Vendor.objects.filter(kosher=True).exists()
    show_vegetarian_filter = Vendor.objects.filter(vegetarian=True).exists()
    
    context = {
        'restaurants': restaurants_qs,
        'available_cuisines': available_cuisines,
        'available_locations': available_locations,
        'show_halal_filter': show_halal_filter,
        'show_kosher_filter': show_kosher_filter,
        'show_vegetarian_filter': show_vegetarian_filter,
        'selected_cuisines': selected_cuisines,
        'selected_locations': selected_locations,
        'halal_filter': halal_filter,
        'kosher_filter': kosher_filter,
        'vegetarian_filter': vegetarian_filter,
    }
    
    return render(request, 'webapp/restaurants.html', context)

def restaurant_detail(request, vendor_id):
    restaurant = get_object_or_404(Vendor, id=vendor_id, vendor_type='restaurant', is_active=True)

    user_rating = None
    if request.user.is_authenticated:
        user_rating = VendorRating.objects.filter(
            user=request.user,
            vendor=restaurant
        ).first()

    context = {
        'restaurant': restaurant,
        'user_rating': user_rating,   # <-- added
    }
    return render(request, 'webapp/restaurant_detail.html', context)

def restaurants(request):
    # Get filter parameters from request
    selected_cuisines = request.GET.getlist('cuisine')
    selected_locations = request.GET.getlist('location')
    halal_filter = request.GET.get('halal') == 'on'
    kosher_filter = request.GET.get('kosher') == 'on'
    vegetarian_filter = request.GET.get('vegetarian') == 'on'
    
    # Start with all restaurants
    restaurants_qs = Vendor.objects.filter(vendor_type__in=['restaurant', 'cafe'])
    
    # Apply filters if they exist
    if selected_cuisines:
        # Filter by cuisine types (ManyToMany relationship)
        restaurants_qs = restaurants_qs.filter(cuisine_types__name__in=selected_cuisines).distinct()
    
    if halal_filter:
        restaurants_qs = restaurants_qs.filter(halal=True)
    
    if kosher_filter:
        restaurants_qs = restaurants_qs.filter(kosher=True)
    
    if vegetarian_filter:
        restaurants_qs = restaurants_qs.filter(vegetarian=True)
    
    if selected_locations:
        # For location filtering
        location_q = Q()
        for location in selected_locations:
            location_q |= Q(address__icontains=location)
        restaurants_qs = restaurants_qs.filter(location_q)
    
    # Sort restaurants alphabetically
    restaurants_qs = restaurants_qs.order_by(Lower('business_name'))
    
    # Get all available cuisines for the filter sidebar
    # Use the correct reverse relationship name 'vendors' (plural)
    available_cuisines = CuisineType.objects.filter(
        vendors__vendor_type__in=['restaurant', 'cafe']  # Changed 'vendor' to 'vendors'
    ).distinct().order_by('name')
    
    # For locations, extract from address field
    available_locations = []
    addresses = Vendor.objects.filter(vendor_type__in=['restaurant', 'cafe']).values_list('address', flat=True)
    for addr in addresses:
        if addr:
            # Try to extract the area/neighborhood from address
            # Common Singapore addresses: "333 Orchard Road, #05-03 Singapore 238867"
            # or "78 Airport Boulevard, #B2-228 Singapore 819666"
            if ',' in addr:
                # Take the part before the first comma
                location = addr.split(',')[0].strip()
                # Remove unit numbers like "#05-03" if present
                if '#' in location:
                    location = location.split('#')[0].strip()
                if location and location not in available_locations:
                    available_locations.append(location)
            else:
                # If no comma, take the first few words
                parts = addr.split()
                if len(parts) > 1:
                    location = ' '.join(parts[:2])  # Take first 2 words
                    if location not in available_locations:
                        available_locations.append(location)
    
    # Determine which dietary filters to show
    restaurant_vendors = Vendor.objects.filter(vendor_type__in=['restaurant', 'cafe'])
    show_halal_filter = restaurant_vendors.filter(halal=True).exists()
    show_kosher_filter = restaurant_vendors.filter(kosher=True).exists()
    show_vegetarian_filter = restaurant_vendors.filter(vegetarian=True).exists()
    
    context = {
        'restaurants': restaurants_qs,
        'available_cuisines': available_cuisines,
        'available_locations': sorted(available_locations),
        'show_halal_filter': show_halal_filter,
        'show_kosher_filter': show_kosher_filter,
        'show_vegetarian_filter': show_vegetarian_filter,
        'selected_cuisines': selected_cuisines,
        'selected_locations': selected_locations,
        'halal_filter': halal_filter,
        'kosher_filter': kosher_filter,
        'vegetarian_filter': vegetarian_filter,
    }
    
    return render(request, 'webapp/restaurants.html', context)

def food_stall_detail(request, vendor_id):
    """View for individual food stall detail page"""
    # Get vendor with type 'stall' and the specified ID
    stall = get_object_or_404(Vendor, id=vendor_id, vendor_type='stall', is_active=True)
    
    # Get user's existing rating if authenticated
    user_rating = None
    if request.user.is_authenticated:
        user_rating = VendorRating.objects.filter(
            user=request.user,
            vendor=stall
        ).first()
    
    # Calculate total reviews
    total_reviews = VendorRating.objects.filter(vendor=stall).count()
    
    # Calculate average rating
    ratings = VendorRating.objects.filter(vendor=stall)
    average_rating = 0.0
    if ratings.exists():
        average_rating = sum(r.rating for r in ratings) / ratings.count()
    
    context = {
        'stall': stall,
        'user_rating': user_rating,
        'total_reviews': total_reviews,
        'average_rating': average_rating,
    }
    
    return render(request, 'webapp/food_stall_detail.html', context)

def food_stalls(request):
    """Food Stalls listing page with filters"""
    # Get filter parameters from request
    selected_cuisines = request.GET.getlist('cuisine')
    halal_filter = request.GET.get('halal') == 'on'
    kosher_filter = request.GET.get('kosher') == 'on'
    vegetarian_filter = request.GET.get('vegetarian') == 'on'
    selected_locations = request.GET.getlist('location')
    
    # Start with all food stalls (vendors with vendor_type='stall')
    stalls_qs = Vendor.objects.filter(vendor_type='stall', is_active=True)
    
    # Apply filters if they exist
    if selected_cuisines:
        # Filter by cuisine type names
        stalls_qs = stalls_qs.filter(cuisine_types__name__in=selected_cuisines).distinct()
    
    if halal_filter:
        stalls_qs = stalls_qs.filter(halal=True)
    
    if kosher_filter:
        stalls_qs = stalls_qs.filter(kosher=True)
    
    if vegetarian_filter:
        stalls_qs = stalls_qs.filter(vegetarian=True)
    
    if selected_locations:
        # Filter by location (address contains location name)
        location_q = Q()
        for location in selected_locations:
            location_q |= Q(address__icontains=location)
        stalls_qs = stalls_qs.filter(location_q)
    
    # Sort stalls alphabetically
    stalls_qs = stalls_qs.order_by(Lower('business_name'))
    
    # Get all available cuisines for the filter sidebar
    # Use the correct field name 'vendors' (plural) instead of 'vendor'
    available_cuisines = CuisineType.objects.filter(
        vendors__vendor_type='stall',
        vendors__is_active=True
    ).distinct().order_by('name')
    
    # Determine which dietary filters to show
    stall_vendors = Vendor.objects.filter(vendor_type='stall', is_active=True)
    show_halal_filter = stall_vendors.filter(halal=True).exists()
    show_kosher_filter = stall_vendors.filter(kosher=True).exists()
    show_vegetarian_filter = stall_vendors.filter(vegetarian=True).exists()
    
    context = {
        'food_stalls': stalls_qs,  # Changed from 'stalls' to 'food_stalls'
        'available_cuisines': available_cuisines,
        'show_halal_filter': show_halal_filter,
        'show_kosher_filter': show_kosher_filter,
        'show_vegetarian_filter': show_vegetarian_filter,
        'selected_cuisines': selected_cuisines,
        'selected_locations': selected_locations,
        'halal_filter': halal_filter,
        'kosher_filter': kosher_filter,
        'vegetarian_filter': vegetarian_filter,
        'page_title': 'Food Stalls - TasteLocal Singapore'
    }
    
    return render(request, 'webapp/food_stalls.html', context)

def culinary_events(request):
    """List all culinary events (pop-ups, tastings, fairs, etc.)"""
    events_list = Event.objects.filter(is_active=True).select_related('vendor')

    # optional cuisine filter
    selected_cuisines = request.GET.getlist('cuisine')
    if selected_cuisines:
        events_list = events_list.filter(event_cuisine__name__in=selected_cuisines).distinct()

    available_cuisines = CuisineType.objects.values_list('name', flat=True).order_by('name')

    context = {
        'events': events_list,          # <-- real Event queryset
        'selected_cuisines': selected_cuisines,
        'available_cuisines': available_cuisines,
    }
    return render(request, 'webapp/culinary_events.html', context)

def culinary_event_detail(request, event_id):
    """View for individual culinary event detail page"""
    # This looks for an EVENT object
    from vendors.models import Event
    event = get_object_or_404(Event, id=event_id, is_active=True)
    
    context = {
        'event': event,  # This is now an Event object
    }
    return render(request, 'webapp/culinary_event_detail.html', context)

# Views for Tours Webapp functions

def tours_experiences(request):
    """Tours & Experiences main page"""
    tours_count = Tour.objects.filter(is_active=True).count()
    featured_tours = Tour.objects.filter(is_featured=True, is_active=True)[:3]
    
    context = {
        'tours_count': tours_count,
        'featured_tours': featured_tours,
        'page_title': 'Tours & Experiences - TasteLocal Singapore'
    }
    return render(request, 'webapp/tours_experiences.html', context)

def guided_tours(request):
    """Guided Food Tours listing page with filters"""
    # Get all active tours
    guided_tours = Tour.objects.filter(is_active=True).select_related('tour_operator')
    
    # Get filter parameters
    selected_tour_types = request.GET.getlist('tour_type')
    selected_operators = request.GET.getlist('operator')
    
    # Apply filters
    if selected_tour_types:
        guided_tours = guided_tours.filter(tour_type__in=selected_tour_types)
    
    if selected_operators:
        guided_tours = guided_tours.filter(tour_operator_id__in=selected_operators)
    
    # Get available options for filters
    available_tour_types = Tour.TOUR_TYPES
    available_operators = TourOperator.objects.filter(
        id__in=guided_tours.values_list('tour_operator_id', flat=True).distinct()
    ).order_by('company_name')
    
    context = {
        'guided_tours': guided_tours,  # Return Tour objects directly
        'selected_tour_types': selected_tour_types,
        'selected_operators': selected_operators,
        'available_tour_types': available_tour_types,
        'available_operators': available_operators,
    }
    return render(request, 'webapp/guided_tours.html', context)

def tour_detail(request, tour_id):
    """Tour detail page - SIMPLE VERSION WITHOUT RATINGS"""
    tour = get_object_or_404(
        Tour.objects.select_related('tour_operator')
                     .prefetch_related('itinerary__vendor'),
        id=tour_id
    )
    
    # Get itinerary items for this tour
    itinerary_items = TourItinerary.objects.filter(
        tour=tour
    ).select_related('vendor').order_by('stop_order')
    
    context = {
        'tour': tour,
    }
    return render(request, 'webapp/tour_detail.html', context)

# Views for Articles & Food Crawls Webapp functions

def foodie_crawls(request):
    """Foodie Crawls page showing articles with Food Crawl keyword"""
    import urllib.parse                      # <- NEW
    print('=== NEW REQUEST ===')             # <- NEW
    print('raw  GET:', request.GET)          # <- NEW
    print('raw  filter list:', request.GET.getlist('filter'))  # <- NEW

    # 1. start with “Food Crawl” articles
    food_crawl_keyword = Keyword.objects.filter(name__iexact="food crawl").first()
    if food_crawl_keyword:
        articles_list = Article.objects.filter(keywords=food_crawl_keyword).order_by('title')
    else:
        articles_list = Article.objects.none()

    # 2. normalise the incoming filter names
    selected_filters = [
        urllib.parse.unquote_plus(f).strip()          # <- NEW (handles + and %20)
        for f in request.GET.getlist('filter')
    ]
    print('cleaned filters:', selected_filters)       # <- NEW

    # 3. apply additional keyword filters
    if selected_filters:
        filter_keywords = []
        for filt in selected_filters:
            kw = Keyword.objects.filter(name__iexact=filt).first()
            print(f'  looking for "{filt}" -> {kw}')  # <- NEW
            if kw:
                filter_keywords.append(kw)

        if filter_keywords:
            for kw in filter_keywords:
                articles_list = articles_list.filter(keywords=kw).distinct()
        else:
            articles_list = Article.objects.none()

    print('final qs count:', articles_list.count())   # <- NEW
    print('===================')                       # <- NEW

    context = {
        'articles': articles_list,
        'selected_filters': selected_filters,
        'available_filters': [
            "Michelin",
            "Lau Pa Sat",
            "Maxwell Food Centre",
            "Newton Food Centre"
        ],
        'page_title': 'Foodie Crawl Articles - TasteLocal Singapore'
    }
    return render(request, 'webapp/foodie_crawls.html', context)

def foodie_stories(request):
    # Get filter parameters from request
    selected_keyword_ids = request.GET.getlist('keyword')
    selected_authors = request.GET.getlist('author')
    selected_years = request.GET.getlist('year')
    
    # Start with all articles - SORTED ALPHABETICALLY
    articles = Article.objects.all().order_by('title')
    
    # Apply filters if they exist
    if selected_keyword_ids:
        articles = articles.filter(keywords__id__in=selected_keyword_ids)
    
    if selected_authors:
        articles = articles.filter(author_name__in=selected_authors)
    
    if selected_years:
        articles = articles.filter(date_written__year__in=selected_years)
    
    # Get all available keywords for the filter sidebar
    available_keywords = Keyword.objects.all()
    
    # Get all unique authors from existing articles
    available_authors = Article.objects.values_list('author_name', flat=True).distinct()
    
    # Get all unique years from existing articles
    available_years = Article.objects.dates('date_written', 'year').order_by('-date_written')
    available_years = [year.year for year in available_years]
    
    context = {
        'articles': articles,
        'available_keywords': available_keywords,
        'available_authors': available_authors,
        'available_years': available_years,
        'selected_keywords': [int(kw_id) for kw_id in selected_keyword_ids if kw_id.isdigit()],
        'selected_authors': selected_authors,
        'selected_years': [int(year) for year in selected_years if year.isdigit()],
    }
    
    return render(request, 'webapp/foodie_stories.html', context)


# Views for Company Pages    
def about_us(request):
    return render(request, 'webapp/about_us.html')

def our_mission(request):
    return render(request, 'webapp/our_mission.html')

def business_partners(request):
    return render(request, 'webapp/business_partners.html')

def contact(request):
    return render(request, 'webapp/contact.html')

# Views for Legal Pages
def privacy_policy(request):
    return render(request, 'webapp/privacy_policy.html')

def terms_service(request):
    return render(request, 'webapp/terms_service.html')

def article_detail(request, slug):
    """Article detail page"""
    article = get_object_or_404(Article, slug=slug)
    
    context = {
        'article': article,
        'page_title': f'{article.title} - TasteLocal Singapore'
    }
    return render(request, 'webapp/article_detail.html', context)

# Views for Vendor Ratings

@login_required
def submit_rating(request, vendor_id):
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, id=vendor_id)
        
        rating = request.POST.get('rating')
        
        # Check if user already rated this vendor
        existing_rating = VendorRating.objects.filter(
            user=request.user, 
            vendor=vendor
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.save()
            messages.success(request, "Your rating has been updated!")
        else:
            # Create new rating
            VendorRating.objects.create(
                user=request.user,
                vendor=vendor,
                rating=rating
            )
            messages.success(request, "Thank you for your rating!")
        
        # Redirect back to the appropriate detail page based on vendor type
        if vendor.vendor_type == 'restaurant':
            return redirect('webapp:restaurant_detail', vendor_id=vendor_id)
        else:
            return redirect('webapp:food_stall_detail', vendor_id=vendor_id)
    
    # If not POST, redirect back
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if vendor.vendor_type == 'restaurant':
        return redirect('webapp:restaurant_detail', vendor_id=vendor_id)
    else:
        return redirect('webapp:food_stall_detail', vendor_id=vendor_id)

# Views for search everything search bar

def search(request):
    """
    Search with primary (AND words in name/title) and secondary (exact phrase anywhere)
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'webapp/search_results.html', {
            'query': '',
            'results': {'primary': [], 'secondary': []},
            'total_results': 0,
            'search_performed': False
        })
    
    # Split for primary AND search
    search_terms = query.split()
    
    results = {'primary': [], 'secondary': []}
    
    # ===== PRIMARY RESULTS: AND word logic in NAME/TITLE only =====
    if search_terms:
        # Build AND conditions for name/title fields only
        q_primary_vendor = Q()
        q_primary_event = Q()
        q_primary_article = Q()
        q_primary_tour = Q()
        
        for term in search_terms:
            q_primary_vendor &= Q(business_name__icontains=term)
            q_primary_event &= Q(event_name__icontains=term)
            q_primary_article &= Q(title__icontains=term)
            q_primary_tour &= Q(name__icontains=term)
        
        # Primary vendors - MUST have ALL terms in business_name
        primary_vendors = Vendor.objects.filter(q_primary_vendor).distinct().order_by('business_name')
        for vendor in primary_vendors:
            results['primary'].append({
                'type': 'vendor',
                'vendor_type': vendor.vendor_type,
                'object_id': vendor.id,
                'title': vendor.business_name,
                'description': vendor.description[:100] + '...' if vendor.description else '',
                'url': reverse('webapp:restaurant_detail', args=[vendor.id]) 
                       if vendor.vendor_type == 'restaurant' 
                       else reverse('webapp:food_stall_detail', args=[vendor.id]),
                'image_url': vendor.business_pix.url if vendor.business_pix else None,
                'category': 'Dining',
                'subtitle': vendor.get_cuisine_types_display(),
                'relevance': 'primary'
            })
        
        # Primary events - MUST have ALL terms in event_name
        primary_events = Event.objects.filter(q_primary_event).distinct().order_by('event_name')
        for event in primary_events:
            results['primary'].append({
                'type': 'event',
                'object_id': event.id,
                'title': event.event_name,
                'description': event.event_description[:100] + '...' if event.event_description else '',
                'url': reverse('webapp:culinary_event_detail', args=[event.id]),
                'image_url': event.event_pix.url if event.event_pix else None,
                'category': 'Events',
                'subtitle': event.display_date_range if hasattr(event, 'display_date_range') else '',
                'relevance': 'primary'
            })
        
        # Primary articles - MUST have ALL terms in title
        primary_articles = Article.objects.filter(q_primary_article).distinct().order_by('title')
        for article in primary_articles:
            results['primary'].append({
                'type': 'article',
                'slug': article.slug,
                'title': article.title,
                'description': article.content[:100] + '...' if article.content else '',
                'url': reverse('webapp:article_detail', args=[article.slug]),
                'image_url': article.images.first().image.url if article.images.first() else None,
                'category': 'Articles',
                'subtitle': f"By {article.author_name}",
                'relevance': 'primary'
            })
        
        # Primary tours - MUST have ALL terms in name
        primary_tours = Tour.objects.filter(q_primary_tour).distinct().order_by('name')
        for tour in primary_tours:
            results['primary'].append({
                'type': 'tour',
                'object_id': tour.id,
                'title': tour.name,
                'description': tour.description[:100] + '...' if tour.description else '',
                'url': reverse('webapp:tour_detail', args=[tour.id]),
                'image_url': tour.tour_pic.url if hasattr(tour, 'tour_pic') and tour.tour_pic else None,
                'category': 'Tours',
                'subtitle': f"{tour.type_display if hasattr(tour, 'type_display') else tour.tour_type}",
                'relevance': 'primary'
            })
    
    # ===== SECONDARY RESULTS: Exact phrase match ANYWHERE =====
    # Search for EXACT query phrase in all relevant fields
    q_secondary_vendor = (
        Q(business_name__icontains=query) |
        Q(description__icontains=query) |
        Q(address__icontains=query)
    )
    
    q_secondary_event = (
        Q(event_name__icontains=query) |
        Q(event_description__icontains=query) |
        Q(event_address__icontains=query)
    )
    
    q_secondary_article = (
        Q(title__icontains=query) |
        Q(content__icontains=query)
    )
    
    q_secondary_tour = (
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    
    # Get all secondary results
    secondary_vendors = Vendor.objects.filter(q_secondary_vendor).exclude(
        id__in=[v['object_id'] for v in results['primary'] if v['type'] == 'vendor']
    ).distinct().order_by('business_name')
    
    secondary_events = Event.objects.filter(q_secondary_event).exclude(
        id__in=[e['object_id'] for e in results['primary'] if e['type'] == 'event']
    ).distinct().order_by('event_name')
    
    secondary_articles = Article.objects.filter(q_secondary_article).exclude(
        slug__in=[a['slug'] for a in results['primary'] if a['type'] == 'article']
    ).distinct().order_by('title')
    
    secondary_tours = Tour.objects.filter(q_secondary_tour).exclude(
        id__in=[t['object_id'] for t in results['primary'] if t['type'] == 'tour']
    ).distinct().order_by('name')
    
    # Add secondary vendors
    for vendor in secondary_vendors:
        # Check if exact phrase is in business_name (higher relevance)
        in_name = query.lower() in vendor.business_name.lower()
        
        results['secondary'].append({
            'type': 'vendor',
            'vendor_type': vendor.vendor_type,
            'object_id': vendor.id,
            'title': vendor.business_name,
            'description': vendor.description[:100] + '...' if vendor.description else '',
            'url': reverse('webapp:restaurant_detail', args=[vendor.id]) 
                   if vendor.vendor_type == 'restaurant' 
                   else reverse('webapp:food_stall_detail', args=[vendor.id]),
            'image_url': vendor.business_pix.url if vendor.business_pix else None,
            'category': 'Dining',
            'subtitle': vendor.get_cuisine_types_display(),
            'relevance': 'exact_name' if in_name else 'exact_other'
        })
    
    # Add secondary events
    for event in secondary_events:
        in_name = query.lower() in event.event_name.lower()
        
        results['secondary'].append({
            'type': 'event',
            'object_id': event.id,
            'title': event.event_name,
            'description': event.event_description[:100] + '...' if event.event_description else '',
            'url': reverse('webapp:culinary_event_detail', args=[event.id]),
            'image_url': event.event_pix.url if event.event_pix else None,
            'category': 'Events',
            'subtitle': event.display_date_range if hasattr(event, 'display_date_range') else '',
            'relevance': 'exact_name' if in_name else 'exact_other'
        })
    
    # Add secondary articles
    for article in secondary_articles:
        in_title = query.lower() in article.title.lower()
        
        results['secondary'].append({
            'type': 'article',
            'slug': article.slug,
            'title': article.title,
            'description': article.content[:100] + '...' if article.content else '',
            'url': reverse('webapp:article_detail', args=[article.slug]),
            'image_url': article.images.first().image.url if article.images.first() else None,
            'category': 'Articles',
            'subtitle': f"By {article.author_name}",
            'relevance': 'exact_title' if in_title else 'exact_content'
        })
    
    # Add secondary tours
    for tour in secondary_tours:
        in_name = query.lower() in tour.name.lower()
        
        results['secondary'].append({
            'type': 'tour',
            'object_id': tour.id,
            'title': tour.name,
            'description': tour.description[:100] + '...' if tour.description else '',
            'url': reverse('webapp:tour_detail', args=[tour.id]),
            'image_url': tour.tour_pic.url if hasattr(tour, 'tour_pic') and tour.tour_pic else None,
            'category': 'Tours',
            'subtitle': f"{tour.type_display if hasattr(tour, 'type_display') else tour.tour_type}",
            'relevance': 'exact_name' if in_name else 'exact_other'
        })
    
    # Sort secondary results: exact matches in name first, then others
    results['secondary'].sort(key=lambda x: (
        0 if x['relevance'] in ['exact_name', 'exact_title'] else 1,
        x['title'].lower()
    ))
    
    return render(request, 'webapp/search_results.html', {
        'query': query,
        'results': results,
        'total_results': len(results['primary']) + len(results['secondary']),
        'primary_count': len(results['primary']),
        'secondary_count': len(results['secondary']),
        'search_performed': True
    })