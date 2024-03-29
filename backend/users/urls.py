from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet

app_name = 'api_users'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
