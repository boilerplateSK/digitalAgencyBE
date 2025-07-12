# views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q
from .models import Service, Testimonial, ContactSubmission
from .serializers import (
    ServiceSerializer, TestimonialSerializer, 
    ContactSubmissionSerializer, ContactSubmissionCreateSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



class ServiceListView(generics.ListAPIView):
    """
    Get all active services ordered by display order
    """
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Disable pagination temporarily
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).order_by('order')
        print(f"ServiceListView queryset count: {queryset.count()}")  # Debug print
        return queryset
        
    def list(self, request, *args, **kwargs):
        """Override list method for debugging"""
        print("ServiceListView.list() called")
        queryset = self.get_queryset()
        print(f"Queryset in list(): {queryset.count()} items")
        
        serializer = self.get_serializer(queryset, many=True)
        print(f"Serializer data: {serializer.data}")
        
        return Response(serializer.data)

class ServiceDetailView(generics.RetrieveAPIView):
    """
    Get specific service by ID
    """
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)

@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
class TestimonialListView(generics.ListAPIView):
    """
    Get all active testimonials, featured ones first
    """
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True)

@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
class FeaturedTestimonialListView(generics.ListAPIView):
    """
    Get only featured testimonials
    """
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True, is_featured=True)

class ContactSubmissionCreateView(generics.CreateAPIView):
    """
    Create a new contact form submission
    """
    serializer_class = ContactSubmissionCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the contact submission
        contact_submission = serializer.save()
        
        # Send email notification (optional)
        # self.send_notification_email(contact_submission)
        
        return Response(
            {
                'message': 'Thank you for your message. We will get back to you soon!',
                'id': contact_submission.id
            },
            status=status.HTTP_201_CREATED
        )
    
    # def send_notification_email(self, contact_submission):
    #     """Send email notification to admin"""
    #     try:
    #         subject = f"New Contact Form Submission from {contact_submission.name}"
    #         message = f"""
    #         New contact form submission received:
            
    #         Name: {contact_submission.name}
    #         Email: {contact_submission.email}
    #         Phone: {contact_submission.phone}
    #         Message: {contact_submission.message}
            
    #         Submitted at: {contact_submission.created_at}
    #         IP Address: {contact_submission.ip_address}
    #         """
            
    #         send_mail(
    #             subject,
    #             message,
    #             settings.DEFAULT_FROM_EMAIL,
    #             [settings.ADMIN_EMAIL],
    #             fail_silently=True,
    #         )
    #     except Exception as e:
    #         # Log error but don't fail the request
    #         print(f"Failed to send notification email: {e}")

@api_view(['GET'])
@permission_classes([AllowAny])
def api_overview(request):
    """
    API overview endpoint showing available endpoints
    """
    api_urls = {
        'Services': {
            'List all services': '/api/services/',
            'Get service by ID': '/api/services/{id}/',
        },
        'Testimonials': {
            'List all testimonials': '/api/testimonials/',
            'List featured testimonials': '/api/testimonials/featured/',
        },
        'Contact': {
            'Submit contact form': '/api/contact/ (POST)',
        }
    }
    
    return Response({
        'message': 'Welcome to the Services API',
        'endpoints': api_urls,
        'documentation': '/api/docs/',
    })

# Admin views (require authentication)
from rest_framework.permissions import IsAuthenticated

class ContactSubmissionListView(generics.ListAPIView):
    """
    List all contact submissions (admin only)
    """
    serializer_class = ContactSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ContactSubmission.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) | 
                Q(message__icontains=search)
            )
        
        return queryset

class ContactSubmissionDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update specific contact submission (admin only)
    """
    serializer_class = ContactSubmissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = ContactSubmission.objects.all()


@csrf_exempt
def debug_services(request):
    """Debug view to check services data"""
    from .models import Service
    
    services = Service.objects.all()
    active_services = Service.objects.filter(is_active=True)
    
    data = {
        'total_services': services.count(),
        'active_services': active_services.count(),
        'all_services': [
            {
                'id': s.id,
                'title': s.title,
                'is_active': s.is_active,
                'order': s.order
            } for s in services
        ]
    }
    
    return JsonResponse(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_services_drf(request):
    """Debug view using DRF to check serialization"""
    from .models import Service
    from .serializers import ServiceSerializer
    
    services = Service.objects.filter(is_active=True)
    print(f"Found {services.count()} active services")
    
    try:
        serializer = ServiceSerializer(services, many=True, context={'request': request})
        serialized_data = serializer.data
        print(f"Serialized data: {serialized_data}")
        
        return Response({
            'count': services.count(),
            'services': serialized_data,
            'raw_data': [{'id': s.id, 'title': s.title} for s in services]
        })
    except Exception as e:
        print(f"Serialization error: {e}")
        return Response({
            'error': str(e),
            'count': services.count(),
            'raw_data': [{'id': s.id, 'title': s.title} for s in services]
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_service_detail(request, pk):
    """Debug individual service"""
    from .models import Service
    from .serializers import ServiceSerializer
    
    try:
        service = Service.objects.get(pk=pk, is_active=True)
        serializer = ServiceSerializer(service, context={'request': request})
        return Response(serializer.data)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)