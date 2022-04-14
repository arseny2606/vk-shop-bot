import json

from vkbottle import GroupEventType
from vkbottle import Keyboard, Callback, KeyboardButtonColor, Text
from vkbottle.bot import Blueprint, MessageEvent

from db.models import Product, Category
from tools.keyboard_generators import generate_products_keyboard
from tools.states import EditProduct, EditCategory

bp = Blueprint("callback buttons")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_callback(event: MessageEvent):
    payload = event.payload
    if not payload:
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    command = payload.get("command")
    if not command:
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    if command == "show_product":
        product_id = payload.get("product_id")
        if product_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            await event.show_snackbar("Такого продукта не существует.")
            return
        category_keyboard = Keyboard(one_time=False, inline=True)
        category_keyboard.add(
            Callback("Изменить", {"command": "edit_product", "product_id": product_id,
                                  "from_page": payload.get("from_page", 1)
                                  }), color=KeyboardButtonColor.PRIMARY).row()
        category_keyboard.add(
            Callback("Удалить", {"command": "delete_product", "product_id": product_id,
                                 "from_page": payload.get("from_page", 1)
                                 }), color=KeyboardButtonColor.NEGATIVE)
        await event.send_message(message=f"Продукт #{product_id}:\n"
                                         f"Название: {product.name}\n"
                                         f"Цена: {float(product.price)} RUB",
                                 keyboard=category_keyboard.get_json())
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    if command == "edit_product":
        product_id = payload.get("product_id")
        if product_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            await event.show_snackbar("Такого продукта не существует.")
            return
        temp_keyboard = Keyboard(inline=True)
        temp_keyboard.add(Text("Оставить"))
        await event.send_message(message=f"Прошлая цена: {float(product.price)} RUB\nВведите цену:",
                                 keyboard=temp_keyboard.get_json())
        await bp.state_dispenser.set(event.user_id, EditProduct.PRICE, product=product,
                                     from_page=payload["from_page"])
    if command == "delete_product":
        product_id = payload.get("product_id")
        if product_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            await event.show_snackbar("Такого продукта не существует.")
            return
        name = product.name
        product.delete()
        await event.show_snackbar(f"Продукт {name} успешно удалён")
        await event.edit_message(peer_id=event.peer_id,
                                 conversation_message_id=event.conversation_message_id,
                                 message="Продукт удалён.",
                                 keyboard=generate_products_keyboard(payload.get("from_page", 1)))
        return
    if command == "show_category":
        category_id = payload.get("category_id")
        if category_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        category = Category.objects.filter(id=category_id).first()
        if not category:
            await event.show_snackbar("Такой категории не существует.")
            return
        category_keyboard = Keyboard(one_time=False, inline=True)
        category_keyboard.add(
            Callback("Изменить", {"command": "edit_category", "category_id": category_id
                                  }), color=KeyboardButtonColor.PRIMARY).row()
        category_keyboard.add(
            Callback("Удалить", {"command": "delete_category", "category_id": category_id
                                 }), color=KeyboardButtonColor.NEGATIVE)
        await event.send_message(message=f"Категория #{category_id}:\n"
                                         f"Название: {category.name}",
                                 keyboard=category_keyboard.get_json())
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    if command == "edit_category":
        category_id = payload.get("category_id")
        if category_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        category = Category.objects.filter(id=category_id).first()
        if not category:
            await event.show_snackbar("Такой категории не существует.")
            return
        temp_keyboard = Keyboard(inline=True)
        temp_keyboard.add(Text("Оставить"))
        await event.send_message(message=f"Прошлое имя: <<{category.name}>>\nВведите новое имя:",
                                 keyboard=temp_keyboard.get_json())
        await bp.state_dispenser.set(event.user_id, EditCategory.EDIT_NAME, category=category)
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    if command == "delete_category":
        category_id = payload.get("category_id")
        if category_id is None:
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return
        category = Category.objects.filter(id=category_id).first()
        if not category:
            await event.show_snackbar("Такой категории не существует.")
            return
        name = category.name
        category.delete()
        await event.show_snackbar(f"Категория {name} успешно удалена")
        await event.edit_message(peer_id=event.peer_id,
                                 conversation_message_id=event.conversation_message_id,
                                 message="Категория удалена.", keyboard=json.dumps({}))
        return
    await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                    user_id=event.user_id,
                                                    peer_id=event.peer_id)
    return
