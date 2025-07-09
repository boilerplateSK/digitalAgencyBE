# tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Service, Testimonial, ContactSubmission

class ServiceModelTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Test Service",
            description="Test description",
            icon="fa-test",
            order=1
        )

    def test_service_creation(self):
        self.assertEqual(self.service.title, "Test Service")
        self.assertTrue(self.service.is_active)
        self.assertEqual(str(self.service), "Test Service")

class TestimonialModelTest(TestCase):
    def setUp(self):
        self.testimonial = Testimonial.objects.create(
            client_name="John Doe",
            client_company="Test Company",
            testimonial_text="Great service!",
            rating=5
        )

    def test_testimonial_creation(self):
        self.assertEqual(self.testimonial.client_name, "John Doe")
        self.assertEqual(self.testimonial.rating, 5)
        self.assertTrue(self.testimonial.is_active)

class ContactSubmissionModelTest(TestCase):
    def setUp(self):
        self.contact = ContactSubmission.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            message="Hello, I need help with my website."
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, "Jane Doe")
        self.assertEqual(self.contact.status, "new")
        self.assertEqual(str(self.contact), "Jane Doe - jane@example.com (new)")

class ServiceAPITest(APITestCase):
    def setUp(self):
        self.service1 = Service.objects.create(
            title="Web Development",
            description="Custom web development",
            icon="fa-code",
            order=1
        )
        self.service2 = Service.objects.create(
            title="Mobile App",
            description="Mobile app development",
            icon="fa-mobile",
            order=2,
            is_active=False
        )

    def test_get_services_list(self):
        url = reverse('service_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active services
        self.assertEqual(response.data[0]['title'], "Web Development")

    def test_get_service_detail(self):
        url = reverse('service_detail', kwargs={'pk': self.service1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Web Development")

    def test_get_inactive_service_detail(self):
        url = reverse('service_detail', kwargs={'pk': self.service2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestimonialAPITest(APITestCase):
    def setUp(self):
        self.testimonial1 = Testimonial.objects.create(
            client_name="John Doe",
            client_company="Company A",
            testimonial_text="Great service!",
            rating=5,
            is_featured=True
        )
        self.testimonial2 = Testimonial.objects.create(
            client_name="Jane Smith",
            client_company="Company B",
            testimonial_text="Good work!",
            rating=4,
            is_featured=False
        )

    def test_get_testimonials_list(self):
        url = reverse('testimonial_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_featured_testimonials(self):
        url = reverse('featured_testimonials')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client_name'], "John Doe")

class ContactAPITest(APITestCase):
    def test_create_contact_submission(self):
        url = reverse('contact_create')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123-456-7890',
            'message': 'This is a test message for contact form.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(ContactSubmission.objects.count(), 1)

    def test_create_contact_submission_invalid_data(self):
        url = reverse('contact_create')
        data = {
            'name': 'A',  # Too short
            'email': 'invalid-email',
            'message': 'Short'  # Too short
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_submission_missing_fields(self):
        url = reverse('contact_create')
        data = {
            'name': 'Test User',
            # Missing email and message
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AdminAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='testpass123'
        )
        self.contact = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message"
        )

    def test_admin_contact_list_requires_auth(self):
        url = reverse('admin_contact_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_contact_list_with_auth(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('admin_contact_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_contact_detail_with_auth(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('admin_contact_detail', kwargs={'pk': self.contact.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test User")

    def test_admin_update_contact_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('admin_contact_detail', kwargs={'pk': self.contact.pk})
        data = {'status': 'replied'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.status, 'replied')

class APIOverviewTest(APITestCase):
    def test_api_overview(self):
        url = reverse('api_overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)