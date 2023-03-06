from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

LENGHT_USER = settings.MODELS_LENGHT_USER
LENGHT_EMAIL = settings.MODELS_LENGHT_EMAIL


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=LENGHT_USER,
        unique=True,
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=LENGHT_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=LENGHT_USER
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LENGHT_USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ('first_name', 'last_name')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='already_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='revent_self_follow',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
