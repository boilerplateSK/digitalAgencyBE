# urls.py
from django.urls import path, include
from . import views

# API URLs
api_urlpatterns = [
    # API Overview
    path('', views.api_overview, name='api_overview'),
    
    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    
    # Testimonials
    path('testimonials/', views.TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/featured/', views.FeaturedTestimonialListView.as_view(), name='featured_testimonials'),
    
    # Contact
    path('contact/', views.ContactSubmissionCreateView.as_view(), name='contact_create'),
    
    # Admin endpoints (require authentication)
    path('admin/contacts/', views.ContactSubmissionListView.as_view(), name='admin_contact_list'),
    path('admin/contacts/<int:pk>/', views.ContactSubmissionDetailView.as_view(), name='admin_contact_detail'),

    path('debug/services/', views.debug_services, name='debug_services'),
    path('debug/services-drf/', views.debug_services_drf, name='debug_services_drf'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]

