import json

from vkbottle import Keyboard, Callback, KeyboardButtonColor, Text
from vkbottle.bot import Blueprint
from vkbottle_types import GroupTypes
from vkbottle_types.events import GroupEventType

from db.models import Product
from tools.states import EditProduct

bp = Blueprint("callback buttons")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_callback(event: GroupTypes.MessageEvent):
    payload = event.object.payload
    if not payload:
        return
    command = payload.get("command")
    if not command:
        return
    if command == "show_product":
        product_id = payload.get("product_id")
        if not product_id:
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            response = {"type": "show_snackbar", "text": "Такого продукта не существует."}
            await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                            user_id=event.object.user_id,
                                                            peer_id=event.object.peer_id,
                                                            event_data=json.dumps(response))
            return
        product_keyboard = Keyboard(one_time=False, inline=True)
        product_keyboard.add(
            Callback("Изменить", {"command": "edit_product", "product_id": product_id
                                  }), color=KeyboardButtonColor.PRIMARY).row()
        product_keyboard.add(
            Callback("Удалить", {"command": "delete_product", "product_id": product_id
                                 }), color=KeyboardButtonColor.NEGATIVE)
        await bp.api.messages.send(user_id=event.object.user_id, random_id=0,
                                   message=f"Продукт #{product_id}:\n"
                                           f"Название: {product.name}\n"
                                           f"Цена: {float(product.price)} RUB",
                                   keyboard=product_keyboard.get_json())
        await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                        user_id=event.object.user_id,
                                                        peer_id=event.object.peer_id)
        return
    if command == "edit_product":
        product_id = payload.get("product_id")
        if not product_id:
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            response = {"type": "show_snackbar", "text": "Такого продукта не существует."}
            await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                            user_id=event.object.user_id,
                                                            peer_id=event.object.peer_id,
                                                            event_data=json.dumps(response))
            return
        temp_keyboard = Keyboard(inline=True)
        temp_keyboard.add(Text("Оставить"))
        await bp.api.messages.send(user_id=event.object.user_id,
                                   random_id=0,
                                   message=f"Прошлая цена: {float(product.price)} RUB\nВведите цену:",
                                   keyboard=temp_keyboard.get_json())
        await bp.state_dispenser.set(event.object.user_id, EditProduct.PRICE, product=product)
    if command == "delete_product":
        product_id = payload.get("product_id")
        if not product_id:
            return
        product = Product.objects.filter(id=product_id).first()
        if not product:
            response = {"type": "show_snackbar", "text": "Такого продукта не существует."}
            await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                            user_id=event.object.user_id,
                                                            peer_id=event.object.peer_id,
                                                            event_data=json.dumps(response))
            return
        name = product.name
        product.delete()
        response = {"type": "show_snackbar", "text": f"Продукт {name} успешно удалён"}
        await bp.api.messages.edit(peer_id=event.object.peer_id,
                                   conversation_message_id=event.object.conversation_message_id,
                                   message="Продукт удалён.",
                                   keyboard=json.dumps({}))
        await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                        user_id=event.object.user_id,
                                                        peer_id=event.object.peer_id,
                                                        event_data=json.dumps(response))
        await bp.state_dispenser.delete(event.object.user_id)
        return
    await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,
                                                    user_id=event.object.user_id,
                                                    peer_id=event.object.peer_id)
    return
