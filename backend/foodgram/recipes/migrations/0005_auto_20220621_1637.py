# Generated by Django 2.2.28 on 2022-06-21 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_favorites'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='single_favorite'),
        ),
    ]
