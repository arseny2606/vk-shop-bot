from vkbottle import BaseStateGroup


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2
    IMAGE = 3


class EditProduct(BaseStateGroup):
    PRICE = 4
    IMAGE = 5


class AddCategory(BaseStateGroup):
    NAME = 6


class EditCategory(BaseStateGroup):
    EDIT_NAME = 7


class AddBalance(BaseStateGroup):
    AMOUNT = 8
    CHECK = 9
