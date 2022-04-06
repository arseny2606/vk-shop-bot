# Generated by Django 3.2.9 on 2022-04-06 19:29

from django.db import migrations


def create_roles(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Role = apps.get_model("db", "Role")
    if not Role.objects.using(db_alias).filter(id=1).count():
        Role.objects.using(db_alias).create(id=1, name="Пользователь", priority=0)
    if not Role.objects.using(db_alias).filter(id=2).count():
        Role.objects.using(db_alias).create(id=2, name="Администратор", priority=80)
    if not Role.objects.using(db_alias).filter(id=5).count():
        Role.objects.using(db_alias).create(id=5, name="Разработчик", priority=110)


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
