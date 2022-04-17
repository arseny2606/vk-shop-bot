from vkbottle import GroupEventType, PhotoMessageUploader
from vkbottle import Keyboard, Callback, KeyboardButtonColor, Text
from vkbottle.bot import Blueprint, MessageEvent

from db.models import Product, Category, User
from tools.keyboard_generators import generate_products_keyboard, generate_categories_keyboard
from tools.qiwi import check_payment
from tools.states import EditProduct, EditCategory, AddBalance

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
        admin = payload.get("admin", True)
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
        if admin:
            category_keyboard.add(
                Callback("Изменить", {"command": "edit_product", "product_id": product_id,
                                      "from_page": payload.get("from_page", 1)
                                      }), color=KeyboardButtonColor.PRIMARY).row()
            category_keyboard.add(
                Callback("Удалить", {"command": "delete_product", "product_id": product_id,
                                     "from_page": payload.get("from_page", 1)
                                     }), color=KeyboardButtonColor.NEGATIVE)
        else:
            category_keyboard.add(
                Callback("Купить", {"command": "buy_product", "product_id": product_id,
                                    "from_page": payload.get("from_page", 1)
                                    }), color=KeyboardButtonColor.POSITIVE)
        if product.image:
            file = await PhotoMessageUploader(bp.api).upload(f"{product.image.path}",
                                                             peer_id=event.peer_id)
            await event.send_message(message=f"Продукт #{product_id}:\n"
                                             f"Название: {product.name}\n"
                                             f"Цена: {float(product.price)} RUB",
                                     keyboard=category_keyboard.get_json(),
                                     attachment=file)
        else:
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
        if product.image():
            product.image.delete()
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
            Callback("Изменить", {"command": "edit_category", "category_id": category_id,
                                  "from_page": payload.get("from_page", 1)
                                  }), color=KeyboardButtonColor.PRIMARY).row()
        category_keyboard.add(
            Callback("Удалить", {"command": "delete_category", "category_id": category_id,
                                 "from_page": payload.get("from_page", 1)
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
        await bp.state_dispenser.set(event.user_id, EditCategory.EDIT_NAME, category=category,
                                     from_page=payload.get('from_page', 1))
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
                                 message="Категория удалена.",
                                 keyboard=generate_categories_keyboard(payload.get('from_page', 1)))
        return
    if command == "check_payment":
        user_profile = User.objects.get_or_create(user_id=event.object.user_id)[0]
        billId = payload.get("billId")
        if billId is None:
            await event.show_snackbar("Счёт не найден.")
            return
        payment = await check_payment(billId)
        status = payment["status"]["value"]
        state = await bp.state_dispenser.get(event.object.peer_id)
        if state is None:
            await event.show_snackbar("Счёт не найден.")
            return
        if status == "PAID" and state.validate_state(AddBalance.CHECK):
            amount = float(payment["amount"]["value"])
            user_profile.balance += amount
            user_profile.save()
            await event.show_snackbar("Ваш баланс успешно пополнен.")
            await bp.state_dispenser.delete(event.object.peer_id)
            await event.send_message(f"Профиль\nБаланс: {user_profile.balance} RUB")
        elif status == "WAITING":
            await event.show_snackbar("Счёт не оплачен.")
        return
    if command == "show_products":
        category_id = payload.get("category_id")
        category = Category.objects.filter(id=category_id).first()
        products = Product.objects.filter(category=category).all()
        page = payload.get("page")
        if page:
            products_list_keyboard = generate_products_keyboard(page, False, products)
            if products_list_keyboard is None:
                await event.send_message(f"Здесь ничего нет.")
                await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                                user_id=event.user_id,
                                                                peer_id=event.peer_id)
            await event.send_message(f"Страница {page}",
                                     keyboard=products_list_keyboard.get_json())
        else:
            products_list_keyboard = generate_products_keyboard(1, False, products)
            if products_list_keyboard is None:
                await event.send_message(f"Здесь ничего нет.")
                await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                                user_id=event.user_id,
                                                                peer_id=event.peer_id)
            await event.send_message("Выберите продукт",
                                     keyboard=products_list_keyboard.get_json())
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    if command == "buy_product":
        user_profile = User.objects.get_or_create(user_id=event.object.user_id)[0]
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
        if user_profile.balance < product.price:
            await event.send_message(f"Недостаточный баланс.")
            await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                            user_id=event.user_id,
                                                            peer_id=event.peer_id)
            return

        user_profile.balance -= product.price
        user_profile.save()
        await event.edit_message(peer_id=event.peer_id,
                                 conversation_message_id=event.conversation_message_id,
                                 message="Товар куплен.")
        await event.show_snackbar("Товар успешно куплен.")
        await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                        user_id=event.user_id,
                                                        peer_id=event.peer_id)
        return
    await bp.api.messages.send_message_event_answer(event_id=event.event_id,
                                                    user_id=event.user_id,
                                                    peer_id=event.peer_id)
    return
