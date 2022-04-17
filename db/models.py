import asyncio
import sys

from tools.utils import getName

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Role(models.Model):
    name = models.CharField(max_length=200)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.name}]"


class User(models.Model):
    user_id = models.IntegerField()
    role = models.ForeignKey(Role, on_delete=models.SET_DEFAULT, default=1)
    balance = models.FloatField(default=0)

    def get_full_name(self, name_case: str = "nom"):
        return ' '.join(asyncio.run(getName(self.user_id, name_case)))

    def get_name(self, name_case: str = "nom"):
        return asyncio.run(getName(self.user_id, name_case))[0]

    def get_push(self, name_case: str = "nom"):
        return f"@id{self.user_id}({self.get_full_name(name_case)})"

    def __str__(self):
        return f"User vk.com/id{self.user_id}, {self.role.name}"


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=1)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default="none")
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name
