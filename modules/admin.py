from vkbottle import Keyboard, Text, KeyboardButtonColor
from vkbottle.bot import Blueprint, rules, Message
from vkbottle_types import BaseStateGroup

from db.models import User, Category, Product

import json

bp = Blueprint("admin menu")
bp.labeler.ignore_case = True
bp.labeler.auto_rules = [rules.PeerRule(from_chat=False)]

main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add(Text("изменить товары", payload={"command": "edit_products"}),
                  color=KeyboardButtonColor.POSITIVE)
main_keyboard.add(Text("изменить категории", payload={"command": "edit_categories"}),
                  color=KeyboardButtonColor.POSITIVE)

products_keyboard = Keyboard(one_time=False, inline=False)
products_keyboard.add(Text("Добавить продукт", payload={"command": "add_product"}),
                      color=KeyboardButtonColor.POSITIVE)
products_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                      color=KeyboardButtonColor.POSITIVE)

categories_keyboard = Keyboard(one_time=False, inline=False)
categories_keyboard.add(Text("Добавить категорию", payload={"command": "add_category"}),
                        color=KeyboardButtonColor.POSITIVE)
categories_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                        color=KeyboardButtonColor.POSITIVE)


@bp.on.message(text=["Админ-панель", "админ-панель"])
@bp.on.message(payload={"command": "admin_panel"})
async def admin_panel(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "admin_panel"
    user_profile.save()
    if user_profile.role.priority >= 80:
        await message.answer("Админ-панель", keyboard=main_keyboard.get_json())


@bp.on.message(text=["изменить товары"])
@bp.on.message(payload={"command": "edit_products"})
async def edit_products(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "edit_products"
    user_profile.save()
    if user_profile.role.priority >= 80:
        products = [f"- {i.name} ({float(i.price)} RUB)\n" for i in Product.objects.all()]
        await message.answer(f"Список продуктов:\n{''.join(products)}", keyboard=products_keyboard.get_json())


class AddProduct(BaseStateGroup):
    NAME = 0
    PRICE = 1
    CATEGORY = 2


@bp.on.message(text=["Добавить продукт", "добавить продукт"])
@bp.on.message(payload={"command": "add_product"})
async def add_product(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_product"
    user_profile.save()
    if user_profile.role.priority >= 80:
        await message.answer(f"Введите имя продукта:", keyboard=products_keyboard.get_json())
        await bp.state_dispenser.set(message.from_id, AddProduct.NAME)


@bp.on.message(state=AddProduct.NAME)
async def add_product_name_handler(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_product"
    user_profile.save()
    if user_profile.role.priority >= 80:
        await message.answer(f"Введите цену:", keyboard=products_keyboard.get_json())
        await bp.state_dispenser.set(message.from_id, AddProduct.PRICE, name=message.text)


@bp.on.message(state=AddProduct.PRICE)
async def add_product_price_handler(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_product"
    user_profile.save()
    temp_keyboard = Keyboard(inline=True)
    for i in Category.objects.all():
        temp_keyboard.add(Text(i.name, payload={"category": f"{i.name}"}))
    if user_profile.role.priority >= 80:
        await message.answer(f"Выберите категорию:", keyboard=temp_keyboard.get_json())
        await bp.state_dispenser.set(message.from_id, AddProduct.CATEGORY, name=message.state_peer.payload['name'],
                                     price=message.text)


@bp.on.message(state=AddProduct.CATEGORY)
async def add_product_category_handler(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_product"
    user_profile.save()
    if user_profile.role.priority >= 80:
        new_product = Product(name=message.state_peer.payload['name'], price=int(message.state_peer.payload['price']),
                              category=Category.objects.get_or_create(name=json.loads(message.payload)["category"])[0])
        new_product.save()
        await message.answer(f"Продукт '{new_product.name}' успешно добавлен", keyboard=products_keyboard.get_json())
        await bp.state_dispenser.delete(message.from_id)
        await edit_products(message)


@bp.on.message(text=["изменить категории"])
@bp.on.message(payload={"command": "edit_categories"})
async def edit_categories(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "edit_categories"
    user_profile.save()
    if user_profile.role.priority >= 80:
        categories = [f"- {i.name}\n" for i in Category.objects.all()]
        await message.answer(f"Список категорий:\n{''.join(categories)}", keyboard=categories_keyboard.get_json())


class AddCategory(BaseStateGroup):
    NAME = 3


@bp.on.message(text=["Добавить категорию", "добавить категорию"])
@bp.on.message(payload={"command": "add_category"})
async def add_category(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_category"
    user_profile.save()
    if user_profile.role.priority >= 80:
        await message.answer(f"Введите имя категории:", keyboard=categories_keyboard.get_json())
        await bp.state_dispenser.set(message.from_id, AddCategory.NAME)


@bp.on.message(state=AddCategory.NAME)
async def add_category_name_handler(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    user_profile.current_state = "add_category"
    user_profile.save()
    if user_profile.role.priority >= 80:
        new_category = Category(name=message.text)
        new_category.save()
        await message.answer(f"Категория '{new_category.name}' успешно добавлена", keyboard=products_keyboard.get_json())
        await bp.state_dispenser.delete(message.from_id)
        await edit_categories(message)
