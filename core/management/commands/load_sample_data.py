# management/commands/load_sample_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Service, Testimonial

class Command(BaseCommand):
    help = 'Load sample data for services and testimonials'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create sample services
        services_data = [
            {
                'title': 'Web Development',
                'description': 'Custom web development solutions using modern frameworks and technologies. From responsive websites to complex web applications.',
                'icon': 'fa-laptop-code',
                'order': 1
            },
            {
                'title': 'Mobile App',
                'description': 'Native and cross-platform mobile app development for iOS and Android. User-friendly apps that engage your audience.',
                'icon': 'fa-mobile-alt',
                'order': 2
            },
            {
                'title': 'SEO Services',
                'description': 'Comprehensive SEO strategies to improve your search engine rankings and drive organic traffic to your website.',
                'icon': 'fa-search',
                'order': 3
            },
            {
                'title': 'Digital Marketing',
                'description': 'Complete digital marketing solutions including social media marketing, PPC campaigns, and content marketing.',
                'icon': 'fa-chart-line',
                'order': 4
            }
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service.title}')
            else:
                self.stdout.write(f'Service already exists: {service.title}')
        
        # Create sample testimonials
        testimonials_data = [
            {
                'client_name': 'Sarah Johnson',
                'client_company': 'Tech Innovations Inc.',
                'client_position': 'CEO',
                'testimonial_text': 'Outstanding service! The team delivered exactly what we needed on time and within budget. Our website looks amazing and performs perfectly.',
                'rating': 5,
                'is_featured': True
            },
            {
                'client_name': 'Michael Chen',
                'client_company': 'Digital Solutions Ltd.',
                'client_position': 'Marketing Director',
                'testimonial_text': 'Professional, reliable, and creative. They helped us increase our online presence significantly. Highly recommended!',
                'rating': 5,
                'is_featured': True
            },
            {
                'client_name': 'Emily Rodriguez',
                'client_company': 'StartUp Hub',
                'client_position': 'Founder',
                'testimonial_text': 'Great communication throughout the project. The mobile app they developed exceeded our expectations and our users love it.',
                'rating': 5,
                'is_featured': True
            },
            {
                'client_name': 'David Wilson',
                'client_company': 'E-commerce Plus',
                'client_position': 'Operations Manager',
                'testimonial_text': 'Their SEO services helped us rank higher on Google and increase our sales by 40%. Amazing results!',
                'rating': 5,
                'is_featured': False
            },
            {
                'client_name': 'Lisa Thompson',
                'client_company': 'Creative Agency',
                'client_position': 'Creative Director',
                'testimonial_text': 'Working with this team was a pleasure. They understood our vision and brought it to life perfectly.',
                'rating': 4,
                'is_featured': False
            }
        ]
        
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                client_name=testimonial_data['client_name'],
                client_company=testimonial_data['client_company'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.client_name}')
            else:
                self.stdout.write(f'Testimonial already exists: {testimonial.client_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )