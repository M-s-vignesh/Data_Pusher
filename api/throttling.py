from rest_framework.throttling import UserRateThrottle

class AuthenticatedUserThrottle(UserRateThrottle):
    rate = '5/s'

    def allow_request(self, request, view):
        if request.user and request.user.is_authenticated:
            return super().allow_request(request, view)
        return True  