from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'is_subscribed',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_anonymous and Follow.objects.filter(
            author__id=obj.id, user__id=user.id
        ).exists()
