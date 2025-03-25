from .serializers import AccountSerializer
from rest_framework import (
                            viewsets,
                            status)
from .models import Account
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class AccountViewset(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = queryset = Account.objects.select_related("created_by", "updated_by").all()
    lookup_field = 'account_id'
    
    @extend_schema(
            description='Create a new Account. Only superusers can create Account.'
            )
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail" : "You don't have access to create an account !" },status= status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail" : "You don't have access to delete an account !" },status= status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)