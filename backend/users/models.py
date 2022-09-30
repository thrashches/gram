from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True,
        verbose_name='Адрес электронной почты',
        help_text='Введите электронную почту'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        blank=False,
        verbose_name='Логин',
        help_text='Введите логин',
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите фамилию'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
