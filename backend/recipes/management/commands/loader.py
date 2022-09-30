import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(f'{settings.BASE_DIR}/data/ingredients.json', 'rb') as f:
            data = json.load(f)

            for value in data:
                ingredient = Ingredient()
                ingredient.name = value['name']
                ingredient.measurement_unit = value['measurement_unit']
                ingredient.save()
        print('Loading is complete.')
