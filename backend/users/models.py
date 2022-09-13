from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import ROLES, STATUS_CHOICES


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        max_length=25,
        verbose_name='role',
        choices=ROLES,
        default='user'
    )
    blocked = models.CharField(
        max_length=10,
        verbose_name='Блокировка',
        choices=STATUS_CHOICES,
        default='Unblock',
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_blocked(self):
        return self.blocked == 'Block'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_following'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
