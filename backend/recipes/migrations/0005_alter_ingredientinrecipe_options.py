# Generated by Django 3.2.7 on 2023-03-02 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230302_1029'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'ordering': ['recipe'], 'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецепте'},
        ),
    ]
