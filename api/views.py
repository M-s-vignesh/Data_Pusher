from .serializers import (AccountSerializer,
                          AccountMemberSerializer,
                          DestinationSerializer,
                          LogSerializer,
                          IncomingDataSerializer)
from rest_framework import (
                            viewsets,
                            status)
from .models import Account,AccountMember,Destination,Log
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema,OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action, api_view
from django.core.cache import cache
from django.utils.http import urlencode
from django.core.exceptions import PermissionDenied
from .tasks import send_data_to_destinations
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.throttling import UserRateThrottle
from .throttling import AuthenticatedUserThrottle

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
    throttle_classes = [AuthenticatedUserThrottle] 

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
    throttle_classes = [AuthenticatedUserThrottle] 
    

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
    

class DestinationViewSet(viewsets.ModelViewSet):
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["account", "http_method", "created_by"]
    search_fields = ["url"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    throttle_classes = [AuthenticatedUserThrottle] 

    def get_queryset(self):
        user = self.request.user
        cache_key = f"destinations_{user.id}_{urlencode(self.request.GET)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        if AccountMember.objects.filter(user=user, role_id=1).exists() or user.is_superuser:
            queryset = Destination.objects.all()
        else:
            user_accounts = AccountMember.objects.filter(user=user).values_list("account_id", flat=True)
            queryset = Destination.objects.filter(account_id__in=user_accounts)
        cache.set(cache_key, queryset, timeout=300) 
        return queryset
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if not AccountMember.objects.filter(user=user, role_id=1).exists() and user.is_superuser:
            return Response({"detail": "You don't have permission to create a destination!"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = request.user
        destination = get_object_or_404(Destination, pk=kwargs["pk"])
        if not AccountMember.objects.filter(user=user, account=destination.account, role_id=2).exists() and not user.is_superuser:
            return Response({"detail": "You can only update destinations linked to your account!"}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not AccountMember.objects.filter(user=user, role_id=1).exists() and not user.is_superuser:
            return Response({"detail": "You don't have permission to delete a destination!"}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)
    
class LogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["account", "destination", "status", "received_timestamp", "processed_timestamp"]
    search_fields = ["event_id"]
    ordering_fields = ["received_timestamp", "processed_timestamp"]
    ordering = ["-received_timestamp"]
    throttle_classes = [AuthenticatedUserThrottle] 

    def get_queryset(self):
        user = self.request.user
        cache_key = f"logs_{user.id}_{urlencode(self.request.GET)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        is_admin = AccountMember.objects.filter(user=user, role_id=1).exists()
        if is_admin:
            queryset = Log.objects.all()
        else:
            user_accounts = AccountMember.objects.filter(user=user).values_list("account_id", flat=True)
            queryset = Log.objects.filter(account_id__in=user_accounts)
        cache.set(cache_key, queryset, timeout=300) 
        return queryset

class IncomingDataHandlerViewSet(viewsets.ViewSet):
    """Handles incoming data processing with caching and rate limiting."""

    throttle_classes = [UserRateThrottle] 

    @extend_schema(
        request=IncomingDataSerializer,  # Define the request schema
        responses={
            status.HTTP_202_ACCEPTED: OpenApiResponse(
                description="Data Received",
                response={"application/json": {"example": {"success": True, "message": "Data Received"}}}
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Duplicate Event ID",
                response={"application/json": {"example": {"success": False, "message": "Duplicate Event ID"}}}
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def incoming_data(self, request):
        serializer = IncomingDataSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data["account"]
        event_id = serializer.validated_data["event_id"]
        data = serializer.validated_data["data"]
        cache_key = f"incoming_data_{account.id}_{event_id}"
        if cache.get(cache_key):
            return Response({"success": False, "message": "Duplicate Event ID"}, status=status.HTTP_400_BAD_REQUEST)
        cache.set(cache_key, True, timeout=60)
        send_data_to_destinations.delay(account.id, event_id, data)
        return Response({"success": True, "message": "Data Received"}, status=status.HTTP_202_ACCEPTED)