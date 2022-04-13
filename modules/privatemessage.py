from vkbottle import Keyboard, Text, KeyboardButtonColor
from vkbottle.bot import Blueprint, rules, Message

from db.models import User

bp = Blueprint("for private messages")
bp.labeler.ignore_case = True
bp.labeler.auto_rules = [rules.PeerRule(from_chat=False)]

main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add(Text("Товары", payload={"command": "products"}),
                  color=KeyboardButtonColor.POSITIVE).row()
main_keyboard.add(Text("Профиль", payload={"command": "profile"}),
                  color=KeyboardButtonColor.POSITIVE).row()

main_admin_keyboard = Keyboard(one_time=False, inline=False)
main_admin_keyboard.add(Text("Товары", payload={"command": "products"}),
                        color=KeyboardButtonColor.POSITIVE).row()
main_admin_keyboard.add(Text("Профиль", payload={"command": "profile"}),
                        color=KeyboardButtonColor.POSITIVE).row()
main_admin_keyboard.add(Text("Админ-панель", payload={"command": "admin_panel"}),
                        color=KeyboardButtonColor.PRIMARY)


@bp.on.message(text=["начать", "Начать"])
@bp.on.message(payload={"command": "start"})
async def start(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    if user_profile.role.priority >= 80:
        await message.answer("Привет!", keyboard=main_admin_keyboard.get_json())
    else:
        await message.answer("Привет!", keyboard=main_keyboard.get_json())


# @bp.on.message()
# async def handle_message(message: Message):
#     await start(message)
