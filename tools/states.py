from vkbottle_types import BaseStateGroup


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2


class EditProduct(BaseStateGroup):
    NAME = 3
    PRICE = 4


class DeleteProduct(BaseStateGroup):
    NAME = 5


class AddCategory(BaseStateGroup):
    NAME = 6


class EditCategory(BaseStateGroup):
    NAME = 7
    EDIT_NAME = 8


class DeleteCategory(BaseStateGroup):
    NAME = 9
