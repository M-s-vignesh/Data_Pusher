from rest_framework import serializers
from .models import Account,AccountMember,Role


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
    
