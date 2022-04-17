from typing import Optional

from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback

from db.models import Product, Category, User


def generate_products_keyboard(page: int = 1, admin: bool = True, products=None) -> Optional[Keyboard]:
    if admin:
        products = Product.objects.all()
    if page < 1:
        return None
    products = products[7 * (page - 1):7 * page]
    if not products:
        return None
    products_list_keyboard = Keyboard(one_time=False, inline=False)
    if admin:
        products_list_keyboard.add(Text("Добавить продукт", payload={"command": "add_product"}),
                                   color=KeyboardButtonColor.PRIMARY).row()
    for product in products:
        products_list_keyboard.add(Callback(f"{product.name} ({float(product.price)} RUB)",
                                            {"command": "show_product",
                                             "product_id": product.id,
                                             "from_page": page,
                                             "admin": admin}),
                                   color=KeyboardButtonColor.POSITIVE).row()
    if admin:
        if page - 1:
            products_list_keyboard.add(
                Text("⬅",
                     payload={"command": "manage_products", "page": page - 1}),
                color=KeyboardButtonColor.SECONDARY)
        products_list_keyboard.add(
            Text("➡",
                 payload={"command": "manage_products", "page": page + 1}),
            color=KeyboardButtonColor.SECONDARY).row()
    else:
        if page - 1:
            products_list_keyboard.add(
                Callback("⬅",
                         payload={"command": "show_products", "page": page - 1}),
                color=KeyboardButtonColor.SECONDARY)
        products_list_keyboard.add(
            Callback("➡",
                     payload={"command": "show_products", "page": page + 1}),
            color=KeyboardButtonColor.SECONDARY).row()
    if admin:
        products_list_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                                   color=KeyboardButtonColor.PRIMARY)
    else:
        products_list_keyboard.add(Text("Назад", payload={"command": "products"}),
                                   color=KeyboardButtonColor.PRIMARY)
    return products_list_keyboard


def generate_categories_keyboard(page: int = 1, admin: bool = True) -> Optional[Keyboard]:
    categories = Category.objects.all()
    if page < 1:
        return None
    categories = categories[7 * (page - 1):7 * page]
    if not categories:
        return None
    categories_list_keyboard = Keyboard(one_time=False, inline=False)
    if admin:
        categories_list_keyboard.add(Text("Добавить категорию", payload={"command": "add_category"}),
                                     color=KeyboardButtonColor.PRIMARY).row()
    for category in categories:
        categories_list_keyboard.add(Callback(f"{category.name}",
                                              {"command": "show_category" if admin else "show_products",
                                               "category_id": category.id,
                                               "from_page": page}),
                                     color=KeyboardButtonColor.POSITIVE).row()
    if page - 1:
        categories_list_keyboard.add(
            Text("⬅",
                 payload={"command": "manage_categories" if admin else "products", "page": page - 1}),
            color=KeyboardButtonColor.SECONDARY)
    categories_list_keyboard.add(
        Text("➡",
             payload={"command": "manage_categories" if admin else "products", "page": page + 1}),
        color=KeyboardButtonColor.SECONDARY).row()
    if admin:
        categories_list_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                                     color=KeyboardButtonColor.PRIMARY)
    else:
        categories_list_keyboard.add(Text("Назад", payload={"command": "start"}),
                                     color=KeyboardButtonColor.PRIMARY)
    return categories_list_keyboard
