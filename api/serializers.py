from rest_framework import serializers
from .models import Account,AccountMember,Role,Destination,Log
from django.utils.timezone import now
import json


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['id','account_id','created_by',
                            'updated_by','created_at','updated_at']
            
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['created_by'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['updated_by'] = user 
        return super().update(instance, validated_data)
    

class AccountMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountMember
        fields = '__all__'
        read_only_fields = ['id','created_by',
                            'updated_by','created_at','updated_at']
            
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['created_by'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['updated_by'] = user 
        return super().update(instance, validated_data)
    
class DestinationSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Destination
        fields = "__all__"
        read_only_fields = ['id','created_by',
                            'updated_by','created_at','updated_at']
            

    def validate_url(self, value):
        """Validate that the URL is properly formatted."""
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError("Invalid URL. Must start with http:// or https://")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['created_by'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['updated_by'] = user 
        return super().update(instance, validated_data)

class LogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Log
        fields = "__all__"


class IncomingDataSerializer(serializers.Serializer):

    data = serializers.JSONField()

    def validate(self, attrs):
        request = self.context["request"]
        headers = request.headers

        app_secret_token = headers.get("CL-X-TOKEN")
        event_id = headers.get("CL-X-EVENT-ID")

        if not app_secret_token:
            raise serializers.ValidationError({"success": False, "message": "Unauthenticated"})
        if not event_id:
            raise serializers.ValidationError({"success": False, "message": "Invalid Data"})

        try:
            account = Account.objects.get(app_secret_token=app_secret_token)
        except Account.DoesNotExist:
            raise serializers.ValidationError({"success": False, "message": "Unauthenticated"})

        attrs["account"] = account
        attrs["event_id"] = event_id
        return attrs