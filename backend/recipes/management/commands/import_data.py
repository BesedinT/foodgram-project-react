from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = 'Loads data'

    def handle(self, *args, **options):

        print('Loading data')

        for row in DictReader(open('../data/ingredients.csv',
                              encoding='utf8')):
            data = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            data.save()
