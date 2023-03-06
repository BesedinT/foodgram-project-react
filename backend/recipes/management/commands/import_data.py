from csv import reader

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = 'Loads data'

    def handle(self, *args, **options):

        print('Loading data')

        with open('../data/ingredients.csv', encoding='utf8') as f:
            print('Loading ingredients')
            csv_reader = reader(f)
            for row_1, row_2 in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row_1,
                    measurement_unit=row_2
                )

        with open('../data/tags.csv', encoding='utf8') as f:
            print('Loading tags')
            csv_reader = reader(f)
            for row_1, row_2, row_3 in csv_reader:
                Tag.objects.get_or_create(
                    name=row_1,
                    color=row_2,
                    slug=row_3
                )

        print('Loading completed')
