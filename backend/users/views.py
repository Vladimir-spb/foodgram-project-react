from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.paginations import CustomPageSizePagination
from api.serializers import FollowSerializer
from users.models import Follow, User
from users.serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPageSizePagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        data = User.objects.filter(following__user=self.request.user).all()
        page = self.paginate_queryset(data)
        serializer = FollowSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if self.request.user == author:
                return Response(
                    {'errors': 'Вы не можете подписываться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Follow.objects.filter(
                    author=author, user=self.request.user
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(author=author, user=self.request.user)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.user == author:
            return Response(
                {'errors': 'Вы не можете отписываться от самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = Follow.objects.filter(
            author=author, user=self.request.user
        )
        if not follow.exists():
            return Response(
                {'errors': 'Вы не подписаны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
