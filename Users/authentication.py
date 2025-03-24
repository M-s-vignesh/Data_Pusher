from rest_framework.authentication import TokenAuthentication

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth:
            user, token = auth
            # Automatically delete token on logout
            if request.method == "POST" and request.path == "/logout/":
                token.delete()
        return auth
