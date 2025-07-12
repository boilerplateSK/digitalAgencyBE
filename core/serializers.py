# serializers.py
from rest_framework import serializers
from .models import Service, Testimonial, ContactSubmission

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'icon', 'order', 'created_at']
        
    def to_representation(self, instance):
        """Override to add debug info"""
        data = super().to_representation(instance)
        print(f"Serializing service: {instance.title} -> {data}")  # Debug print
        return data

class TestimonialSerializer(serializers.ModelSerializer):
    client_image_url = serializers.URLField(source='client_image', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_company', 'client_position', 
            'testimonial_text', 'rating', 'client_image_url', 'is_featured',
            'created_at'
        ]

class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_email(self, value):
        return value.lower()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()

class ContactSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'phone', 'message']
    
    def validate_email(self, value):
        return value.lower()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    # def validate_message(self, value):
    #     if len(value.strip()) < 10:
    #         raise serializers.ValidationError("Message must be at least 10 characters long.")
    #     return value.strip()

    def create(self, validated_data):
        # Add IP address and user agent from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip