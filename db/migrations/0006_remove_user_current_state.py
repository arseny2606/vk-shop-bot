# Generated by Django 3.2.12 on 2022-04-10 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0005_category_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='current_state',
        ),
    ]
