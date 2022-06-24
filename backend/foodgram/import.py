import os
import sqlite3

import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient


def import_category():
    dataset = pd.read_csv('data/ingredients.csv')
    items = []
    for i, row in dataset.iterrows():
        items.append(Ingredient(
            name=row['name'],
            measurement_unit=row['measurement_unit']
        ))
    Ingredient.objects.all().delete()
    Ingredient.objects.bulk_create(items)
    return print('Список категорий успешно импортирован')

if __name__ == '__main__':
    import_category()