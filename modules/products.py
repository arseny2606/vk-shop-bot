import json

from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback
from vkbottle.bot import Blueprint, rules, Message

from db.models import Category, Product
from tools.keyboard_generators import generate_products_keyboard, generate_categories_keyboard
from tools.states import AddCategory, AddProduct, EditProduct, EditCategory
from tools.utils import check_role

bp = Blueprint("products menu")
bp.labeler.ignore_case = True
bp.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add(Text("Назад", payload={"command": "start"}),
                  color=KeyboardButtonColor.PRIMARY)


@bp.on.message(text=["Товары", "товары"])
@bp.on.message(payload={"command": "products"})
async def products(message: Message, page: int = 1):
    categories_list_keyboard = generate_categories_keyboard(page, False)
    if categories_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Выберите категорию",
                         keyboard=categories_list_keyboard.get_json())


@bp.on.message(payload_map={"command": "products", "page": int})
async def products_page(message: Message):
    payload = json.loads(message.payload)
    page = payload["page"]
    categories_list_keyboard = generate_categories_keyboard(page, False)
    if categories_list_keyboard is None:
        return "Здесь ничего нет."
    await message.answer(f"Страница {page}",
                         keyboard=categories_list_keyboard.get_json())
