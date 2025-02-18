import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
INGREDIENTS_FILE = os.path.join(DATA_DIR, 'ingredients.csv')


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла в базу данных'

    def handle(self, *args, **kwargs):
        try:
            with open(INGREDIENTS_FILE, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients = []
                for row in reader:
                    try:
                        name, measurement_unit = row[0].strip(), row[1].strip()
                        ingredients.append(
                            Ingredient(
                                name=name, measurement_unit=measurement_unit
                            )
                        )
                    except IndexError:
                        self.stderr.write(
                            self.style.ERROR(f'Неверный формат строки: {row}')
                        )
                Ingredient.objects.bulk_create(
                    ingredients, ignore_conflicts=True
                )
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы'
            ))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                f'Файл [{INGREDIENTS_FILE}] не найден'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Произошла ошибка: {str(e)}'))
