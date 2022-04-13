from vkbottle_types import BaseStateGroup


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2


class EditProduct(BaseStateGroup):
    PRICE = 3


class AddCategory(BaseStateGroup):
    NAME = 4


class EditCategory(BaseStateGroup):
    EDIT_NAME = 5
