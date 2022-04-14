import json

from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback
from vkbottle.bot import Blueprint, rules, Message

from db.models import Category, Product
from tools.keyboard_generators import generate_products_keyboard, generate_categories_keyboard
from tools.states import AddCategory, AddProduct, EditProduct, EditCategory
from tools.utils import check_role

bp = Blueprint("admin menu")
bp.labeler.ignore_case = True
bp.labeler.auto_rules = [rules.PeerRule(from_chat=False)]

main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add(Text("Управление продуктами", payload={"command": "manage_products"}),
                  color=KeyboardButtonColor.POSITIVE)
main_keyboard.add(Text("Управление категориями", payload={"command": "manage_categories"}),
                  color=KeyboardButtonColor.POSITIVE).row()
main_keyboard.add(Text("Назад", payload={"command": "start"}),
                  color=KeyboardButtonColor.PRIMARY)

products_keyboard = Keyboard(one_time=False, inline=False)
products_keyboard.add(Text("Добавить продукт", payload={"command": "add_product"}),
                      color=KeyboardButtonColor.POSITIVE).row()
products_keyboard.add(Text("Изменить продукт", payload={"command": "edit_product"}),
                      color=KeyboardButtonColor.POSITIVE).row()
products_keyboard.add(Text("Удалить продукт", payload={"command": "delete_product"}),
                      color=KeyboardButtonColor.POSITIVE).row()
products_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                      color=KeyboardButtonColor.PRIMARY)

categories_keyboard = Keyboard(one_time=False, inline=False)
categories_keyboard.add(Text("Добавить категорию", payload={"command": "add_category"}),
                        color=KeyboardButtonColor.POSITIVE).row()
categories_keyboard.add(
    Text("Изменить категорию", payload={"command": "edit_category"}),
    color=KeyboardButtonColor.POSITIVE).row()
categories_keyboard.add(
    Text("Удалить категорию", payload={"command": "delete_category"}),
    color=KeyboardButtonColor.POSITIVE).row()
categories_keyboard.add(Text("Назад", payload={"command": "admin_panel"}),
                        color=KeyboardButtonColor.PRIMARY)


@bp.on.message(text=["Админ-панель", "админ-панель"])
@bp.on.message(payload={"command": "admin_panel"})
@check_role(priority=80)
async def admin_panel(message: Message):
    await message.answer("Админ-панель", keyboard=main_keyboard.get_json())


@bp.on.message(text=["Управление продуктами", "управление продуктами"])
@bp.on.message(payload={"command": "manage_products"})
@check_role(priority=80)
async def manage_products(message: Message, page: int = 1):
    products_list_keyboard = generate_products_keyboard(page)
    if products_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Меню управления продуктами",
                         keyboard=products_list_keyboard.get_json())


@bp.on.message(payload_map={"command": "manage_products", "page": int})
@check_role(priority=80)
async def manage_products_page(message: Message):
    payload = json.loads(message.payload)
    page = payload["page"]
    products_list_keyboard = generate_products_keyboard(page)
    if products_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Страница {page}",
                         keyboard=products_list_keyboard.get_json())


@bp.on.message(text=["Добавить продукт", "добавить продукт"])
@bp.on.message(payload={"command": "add_product"})
@check_role(priority=80)
async def add_product(message: Message):
    await message.answer(f"Введите имя продукта:", keyboard=products_keyboard.get_json())
    await bp.state_dispenser.set(message.from_id, AddProduct.NAME)


@bp.on.message(text=["Управление категориями", "управление категориями"])
@bp.on.message(payload={"command": "manage_categories"})
@check_role(priority=80)
async def manage_categories(message: Message, page: int = 1):
    categories_list_keyboard = generate_categories_keyboard(page)
    if categories_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Меню управления категориями.",
                         keyboard=categories_list_keyboard.get_json())


@bp.on.message(payload_map={"command": "manage_categories", "page": int})
@check_role(priority=80)
async def manage_categories_page(message: Message):
    payload = json.loads(message.payload)
    page = payload["page"]
    categories_list_keyboard = generate_categories_keyboard(page)
    if categories_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Страница {page}",
                         keyboard=categories_list_keyboard.get_json())


@bp.on.message(text=["Добавить категорию", "добавить категорию"])
@bp.on.message(payload={"command": "add_category"})
@check_role(priority=80)
async def add_category(message: Message):
    await message.answer(f"Введите имя категории:")
    await bp.state_dispenser.set(message.from_id, AddCategory.NAME)


@bp.on.message(state=EditProduct.PRICE)
@check_role(priority=80)
async def edit_product_price_handler(message: Message):
    product = message.state_peer.payload['product']
    page = message.state_peer.payload.get('from_page', 1)
    if message.text != "Оставить":
        product.price = float(message.text)
        product.save()
    await message.answer(f"Продукт <<{product.name}>> успешно изменён")
    await manage_products(message, page)
    await bp.state_dispenser.delete(message.from_id)


@bp.on.message(state=AddProduct.NAME)
@check_role(priority=80)
async def add_product_name_handler(message: Message):
    await message.answer(f"Введите цену:", keyboard=products_keyboard.get_json())
    await bp.state_dispenser.set(message.from_id, AddProduct.PRICE, name=message.text)


@bp.on.message(state=AddProduct.PRICE)
@check_role(priority=80)
async def add_product_price_handler(message: Message):
    temp_keyboard = Keyboard(inline=True)
    for i in Category.objects.all():
        temp_keyboard.add(Text(i.name, payload={"category": f"{i.name}"}))
    await message.answer(f"Выберите категорию:", keyboard=temp_keyboard.get_json())
    await bp.state_dispenser.set(message.from_id, AddProduct.CATEGORY,
                                 name=message.state_peer.payload['name'],
                                 price=message.text)


@bp.on.message(state=AddProduct.CATEGORY)
@check_role(priority=80)
async def add_product_category_handler(message: Message):
    new_product = Product(name=message.state_peer.payload['name'],
                          price=int(message.state_peer.payload['price']),
                          category=Category.objects.get_or_create(
                              name=json.loads(message.payload)["category"])[0])
    new_product.save()
    await message.answer(f'Продукт <<{new_product.name}>> успешно добавлен',
                         keyboard=products_keyboard.get_json())
    await bp.state_dispenser.delete(message.from_id)
    await manage_products(message)


@bp.on.message(state=EditCategory.EDIT_NAME)
@check_role(priority=80)
async def edit_category_name_handler(message: Message):
    category = message.state_peer.payload['category']
    page = message.state_peer.payload.get('from_page', 1)
    if message.text != "Оставить":
        category.name = message.text
        category.save()
    await message.answer(f"Категория <<{category.name}>> успешно изменена")
    await manage_categories(message, page)
    await bp.state_dispenser.delete(message.from_id)


@bp.on.message(state=AddCategory.NAME)
@check_role(priority=80)
async def add_category_name_handler(message: Message):
    new_category = Category(name=message.text)
    new_category.save()
    await message.answer(f"Категория <<{new_category.name}>> успешно добавлена",
                         keyboard=products_keyboard.get_json())
    await bp.state_dispenser.delete(message.from_id)
    await manage_categories(message)
