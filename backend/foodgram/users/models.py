from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_registration'
            )
        ]


class Follow(models.Model):
    following = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='автор рецепта',
        on_delete=models.CASCADE
        )
    follower = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='читатель рецепта',
        on_delete=models.CASCADE
        )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['following', 'follower'],
                name='unique_following',
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow',
            ),
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.following}'
