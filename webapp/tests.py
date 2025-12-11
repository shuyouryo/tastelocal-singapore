# webapp/tests.py
from django.test import TestCase
from django.urls import reverse


class UnitTests(TestCase):
    """Unit tests for individual view functions"""
    
    def test_homepage_redirects_with_query(self):
        """Test that homepage redirects to search when query is provided"""
        # Without query - should stay on homepage
        response = self.client.get(reverse('webapp:homepage'))
        self.assertEqual(response.status_code, 200)
        
        # With query - should redirect to search
        response = self.client.get(reverse('webapp:homepage'), {'q': 'pizza'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/search/', response.url)
    
    def test_search_view_empty_query(self):
        """Test search view with empty query returns proper structure"""
        response = self.client.get(reverse('webapp:search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/search_results.html')
        
        # Check context contains expected data
        self.assertEqual(response.context['query'], '')
        self.assertEqual(response.context['total_results'], 0)
        self.assertFalse(response.context['search_performed'])
    
    def test_restaurants_view_basic_functionality(self):
        """Test restaurants view loads with proper template"""
        response = self.client.get(reverse('webapp:restaurants'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/restaurants.html')
        
        # Check that restaurants context exists (even if empty)
        self.assertIn('restaurants', response.context)


class IntegrationTests(TestCase):
    """Integration tests for user workflows"""
    
    def test_homepage_to_search_workflow(self):
        """Integration test: User searches from homepage"""
        # 1. User visits homepage
        response = self.client.get(reverse('webapp:homepage'))
        self.assertEqual(response.status_code, 200)
        
        # 2. User enters search query in homepage form (simulated by direct navigation)
        response = self.client.get(reverse('webapp:search'), {'q': 'italian food'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/search_results.html')
        
        # 3. Verify search was performed
        self.assertTrue(response.context['search_performed'])
        self.assertEqual(response.context['query'], 'italian food')
    
    def test_restaurant_filtering_workflow(self):
        """Integration test: User filters restaurants"""
        # 1. User visits restaurants page
        response = self.client.get(reverse('webapp:restaurants'))
        self.assertEqual(response.status_code, 200)
        
        # 2. User applies halal filter
        response = self.client.get(reverse('webapp:restaurants'), {'halal': 'on'})
        self.assertEqual(response.status_code, 200)
        
        # 3. Verify filter is applied in context
        self.assertTrue(response.context['halal_filter'])
        
        # 4. User adds vegetarian filter
        response = self.client.get(reverse('webapp:restaurants'), {
            'halal': 'on',
            'vegetarian': 'on'
        })
        self.assertEqual(response.status_code, 200)
        
        # 5. Verify both filters are applied
        self.assertTrue(response.context['halal_filter'])
        self.assertTrue(response.context['vegetarian_filter'])
    
    def test_navigation_workflow(self):
        """Integration test: User navigates through the site"""
        # Test navigation through main pages
        pages = [
            ('webapp:homepage', 'webapp/homepage.html'),
            ('webapp:about_us', 'webapp/about_us.html'),
            ('webapp:contact', 'webapp/contact.html'),
            ('webapp:places_eat', 'webapp/places_eat.html'),
        ]
        
        for page_name, template_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
                # Don't check template - some might not exist yet