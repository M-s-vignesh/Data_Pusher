from django.urls import path,include
from rest_framework import permissions,routers
from  Users.views import (UserListView,
                          obtain_auth_token_form,
                          LogoutView,
                          )
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.conf import settings
from drf_spectacular.views import SpectacularSwaggerView
from django.views.generic import TemplateView
from .views import CustomSwaggerView
    
router = routers.DefaultRouter()
router.register(r'users',UserListView, basename='user')
    
urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path('obtain-token/', obtain_auth_token_form,name='obtain_token'),

    path('',include(router.urls)),

     path('swagger/',  CustomSwaggerView.as_view(url_name="schema"), name='swagger-ui'),

    path('logout/', LogoutView.as_view(), name='logout'),
]   
