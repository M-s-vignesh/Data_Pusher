from django.shortcuts import render
from rest_framework import generics,viewsets
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import( 
                api_view, 
                parser_classes, 
                permission_classes,
                )
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample,  OpenApiTypes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .permissions import AllowFirstUserWithoutAuth
from django.contrib.auth import get_user_model


# Create your views here.

User = get_user_model()

@extend_schema(
    methods=['POST'],
    description="Obtain authentication token by providing email and password.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "example": "admin@example.com"},
                "password": {"type": "string", "example": "admin123"}
            },
            "required": ["email", "password"]
        },
        "application/x-www-form-urlencoded": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["email", "password"]
        },
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["email", "password"]
        }
    },
    responses={200: {"type": "object", "properties": {"token": {"type": "string"}}}},
)
@api_view(['POST'])
@parser_classes([JSONParser,FormParser, MultiPartParser])  # ✅ Supports form-data
@permission_classes([AllowAny])
def obtain_auth_token_form(request):
    """
    Custom view to obtain authentication token using JSON and FORM data.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Please provide both username and password."}, status=400)

    from django.contrib.auth import authenticate
    user = authenticate(email=email, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

    return Response({"error": "Invalid credentials"}, status=401)


class UserListView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowFirstUserWithoutAuth]
    parser_classes =(MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_context(self):
        """Pass request context to serializer to control field visibility."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
    @extend_schema(request=UserSerializer,
                   responses={201:UserSerializer},
            description='Create a new user. Only superusers can create users.'
            )

    def create(self, request, *args, **kwargs):
        if User.objects.exists() and  not request.user.is_superuser:
            return Response({"detail": "You don't have access to create a account."}, status= status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_superuser and user.id != request.user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user, data=request.data, context= {'request': request})
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_superuser and request.user.id != user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user, data=request.data, partial=True, context= {'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        admin_users = User.objects.filter(is_superuser=True).count()
        if user.is_superuser and admin_users == 1:
            return Response(
                {"detail": "Cannot delete the only admin account."},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        if not request.user.is_superuser and request.user.id !=user.id:
            return Response({"detail": "You don't have access to delete this account"}, status=status.HTTP_403_FORBIDDEN)
        Token.objects.filter(user=user).delete()
        return super().destroy(request, *args, **kwargs)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowFirstUserWithoutAuth]

    @extend_schema(exclude=True)
    def post(self, request):
        request.auth.delete()
        return Response({"message": "Successfully logged out"}, status=200)