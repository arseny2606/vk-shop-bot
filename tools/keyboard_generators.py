from typing import Optional

from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback

from db.models import Product, Category


def generate_products_keyboard(page: int = 1) -> Optional[Keyboard]:
    products = Product.objects.all()
    if page < 1:
        return None
    products = products[7 * (page - 1):7 * page]
    if not products:
        return None
    products_list_keyboard = Keyboard(one_time=False, inline=False)
    products_list_keyboard.add(Text("Добавить продукт", payload={"command": "add_product"}),
                               color=KeyboardButtonColor.PRIMARY).row()
    for product in products:
        products_list_keyboard.add(Callback(f"{product.name} ({float(product.price)} RUB)",
                                            {"command": "show_product", "product_id": product.id}),
                                   color=KeyboardButtonColor.POSITIVE).row()
    if page - 1:
        products_list_keyboard.add(
            Text("⬅",
                 payload={"command": "manage_products", "page": page - 1}),
            color=KeyboardButtonColor.SECONDARY)
    products_list_keyboard.add(
        Text("➡",
             payload={"command": "manage_products", "page": page + 1}),
        color=KeyboardButtonColor.SECONDARY).row()
    products_list_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                               color=KeyboardButtonColor.PRIMARY)
    return products_list_keyboard


def generate_categories_keyboard(page: int = 1) -> Optional[Keyboard]:
    categories = Category.objects.all()
    if page < 1:
        return None
    categories = categories[7 * (page - 1):7 * page]
    if not categories:
        return None
    categories_list_keyboard = Keyboard(one_time=False, inline=False)
    categories_list_keyboard.add(Text("Добавить категорию", payload={"command": "add_category"}),
                                 color=KeyboardButtonColor.PRIMARY).row()
    for category in categories:
        categories_list_keyboard.add(Callback(f"{category.name}",
                                              {"command": "show_category",
                                               "category_id": category.id}),
                                     color=KeyboardButtonColor.POSITIVE).row()
    if page - 1:
        categories_list_keyboard.add(
            Text("⬅",
                 payload={"command": "manage_categories", "page": page - 1}),
            color=KeyboardButtonColor.SECONDARY)
    categories_list_keyboard.add(
        Text("➡",
             payload={"command": "manage_categories", "page": 2}),
        color=KeyboardButtonColor.SECONDARY).row()
    categories_list_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                                 color=KeyboardButtonColor.PRIMARY)
    return categories_list_keyboard
