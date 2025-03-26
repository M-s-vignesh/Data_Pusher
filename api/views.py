from .serializers import AccountSerializer,AccountMemberSerializer
from rest_framework import (
                            viewsets,
                            status)
from .models import Account,AccountMember
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.cache import cache
from django.utils.http import urlencode
from django.core.exceptions import PermissionDenied

CACHE_KEYS = "accounts_list_keys"

class AccountViewset(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = queryset = Account.objects.select_related("created_by", "updated_by").all()
    lookup_field = 'account_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_name', 'created_by', 'updated_by']
    search_fields = ['account_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.GET.dict()  
        cache_key = f"accounts_list_{user.id}_{urlencode(query_params)}"  

        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data  
        
        is_admin = AccountMember.objects.filter(user=user, role__role_name="Admin").exists()
        if is_admin or user.is_superuser:
            queryset = Account.objects.select_related("created_by", "updated_by").all()
        else:
            account_ids = AccountMember.objects.filter(user=user).values_list("account_id", flat=True)
            queryset = Account.objects.filter(id__in=account_ids)
        valid_fields = {field.name for field in Account._meta.fields}  
        filters = {key: value for key, value in query_params.items() if key in valid_fields}
        queryset = queryset.filter(**filters)
        if not queryset.exists():
            raise PermissionDenied("No accounts Found!")
        keys = cache.get(CACHE_KEYS, set())
        keys.add(cache_key)
        cache.set(CACHE_KEYS, keys, timeout=300) 
        cache.set(cache_key, queryset, timeout=300)
        return queryset
    
    @extend_schema(
            description='Create a new Account. Only superusers can create Account.'
            )
    def create(self, request, *args, **kwargs):
        user = request.user
        is_admin = AccountMember.objects.filter(user=user, role__role_name="Admin").exists()
        if not user.is_superuser and not is_admin:
            return Response({"detail" : "You don't have access to create an account !" },status= status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        account = self.get_object()
        if not user.is_superuser:
            is_admin = AccountMember.objects.filter(user=user, role__role_name="Admin").exists()
            if not is_admin:
                acc_member = AccountMember.objects.filter(user=user, account=account)
                if not acc_member.exists():
                    return Response({"detail" : "You don't have access to update this account !" },status= status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        is_admin = AccountMember.objects.filter(user=user, role__role_name="Admin").exists()
        if not user.is_superuser and not is_admin:
            return Response({"detail" : "You don't have access to delete an account !" },status= status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    

class AccountMemberViewset(viewsets.ModelViewSet):
    serializer_class = AccountMemberSerializer
    permission_classes = [IsAuthenticated]
    queryset = queryset = AccountMember.objects.select_related("created_by", "updated_by").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'user','created_by', 'updated_by']
    search_fields = ['account']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']
    

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.GET.dict()  
        cache_key = f"accounts_member_{user.id}_{urlencode(query_params)}"  
        is_admin = AccountMember.objects.filter(user=user, role__role_name="Admin").exists()
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data  

        if is_admin or user.is_superuser:
            queryset = AccountMember.objects.select_related("created_by", "user", "updated_by").all()
        else:
            user_accounts = AccountMember.objects.filter(user=user).values_list('account_id', flat=True)
            queryset = AccountMember.objects.select_related("created_by", "user", "updated_by").filter(account_id__in=user_accounts)
        valid_fields = {field.name for field in AccountMember._meta.fields}  
        filters = {key: value for key, value in query_params.items() if key in valid_fields}
        queryset = queryset.filter(**filters)
        if not queryset.exists():
            raise PermissionDenied("No accounts Found!")
        keys = cache.get(CACHE_KEYS, set())
        keys.add(cache_key)
        cache.set(CACHE_KEYS, keys, timeout=300) 
        cache.set(cache_key, queryset, timeout=300)
        return queryset
    
    @extend_schema(
            description="""Create Account Member. Only Admin can create Account Members. Give Role as 1 for Admin account and 2 for Normal User account"""
            )
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            is_admin = AccountMember.objects.filter(user=request.user, role__id=1).exists()
            if not is_admin:
                return Response(
                    {"detail": "You don't have access to create an account!"},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            is_admin = AccountMember.objects.filter(user=request.user, role__id=1).exists()
            if not is_admin:
                return Response(
                    {"detail": "You don't have access to update an account!"},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            is_admin = AccountMember.objects.filter(user=request.user, role__id=1).exists()
            if not is_admin:
                return Response(
                    {"detail": "You don't have access to delete an account!"},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().destroy(request, *args, **kwargs)
    
    