from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema_field
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id','email','is_superuser','password',
                'created_by','updated_by','created_at','updated_at']
        read_only_fields = ['id','is_superuser','created_by',
                            'updated_by','created_at','updated_at']
            
    def validate(self, attrs):
        """function to validate password if user is creating account for 
            first time, if they are updating thier account password will
            be by-passed"""
        if self.instance is None and 'password' not in attrs:
            raise serializers.ValidationError({"password" : "This Field is required."})
        return attrs

    def create(self, validated_data):
        if not User.objects.exists():
            validated_data.setdefault("is_superuser", True)
            validated_data.setdefault("is_staff", True)
        validated_data['password'] = make_password(validated_data['password'])
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['created_by'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['updated_by'] = user 
        return super().update(instance, validated_data)
    

