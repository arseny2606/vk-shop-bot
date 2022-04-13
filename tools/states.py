from vkbottle_types import BaseStateGroup


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2


class EditProduct(BaseStateGroup):
    NAME = 3
    PRICE = 4
    CATEGORY = 5


class AddCategory(BaseStateGroup):
    NAME = 6
