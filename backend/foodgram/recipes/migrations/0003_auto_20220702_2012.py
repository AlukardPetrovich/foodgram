# Generated by Django 4.0.5 on 2022-06-27 12:50

import json

from django.db import migrations


def add_ingredients_in_db(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    with open('data/Ingredient.json') as file:
        data = json.load(file)
        list = [
            Ingredient(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'] 
            ) for ingredient in data
        ]
        Ingredient.objects.bulk_create(list)



class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220702_2009'),
    ]


    operations = [
        migrations.RunPython(add_ingredients_in_db),
    ]