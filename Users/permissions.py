from rest_framework.permissions import BasePermission
from Users.models import User

class AllowFirstUserWithoutAuth(BasePermission):
    """
    Custom permission to allow unauthenticated access only for the first user.
    """
    
    def has_permission(self, request, view):
        if request.method == "POST" and not User.objects.exists():
            return True
        return request.user and request.user.is_authenticated 
