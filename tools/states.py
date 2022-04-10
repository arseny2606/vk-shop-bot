from vkbottle_types import BaseStateGroup


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2


class AddCategory(BaseStateGroup):
    NAME = 3
