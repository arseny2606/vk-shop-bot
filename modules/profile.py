from vkbottle import Keyboard, Text, KeyboardButtonColor, OpenLink, Callback
from vkbottle.bot import Blueprint, rules, Message

from db.models import User
from tools.states import AddBalance
from tools.qiwi import create_payment

bp = Blueprint("profile menu")
bp.labeler.ignore_case = True
bp.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add(Text("Пополнить баланс", payload={"command": "add_balance"}),
                  color=KeyboardButtonColor.POSITIVE)
main_keyboard.add(Text("Назад", payload={"command": "start"}),
                  color=KeyboardButtonColor.PRIMARY)


@bp.on.message(text=["Профиль", "профиль"])
@bp.on.message(payload={"command": "profile"})
async def profile(message: Message):
    user_profile = User.objects.get_or_create(user_id=message.from_id)[0]
    await message.answer(f"Профиль\nБаланс: {user_profile.balance} RUB", keyboard=main_keyboard.get_json())


@bp.on.message(text=["Пополнить баланс", "пополнить баланс"])
@bp.on.message(payload={"command": "add_balance"})
async def add_balance(message: Message):
    await message.answer(f"Введите сумму пополнения:", keyboard=main_keyboard.get_json())
    await bp.state_dispenser.set(message.from_id, AddBalance.AMOUNT)


@bp.on.message(state=AddBalance.AMOUNT)
async def add_balance_amount_handler(message: Message):
    amount = float(message.text)
    payment = await create_payment(amount, "Пополнение баланса бота vkshopbot")
    temp_keyboard = Keyboard(inline=True)
    temp_keyboard.add(OpenLink(payment["payUrl"], "Оплатить"))
    await message.answer(f"Оплатите счёт по нажатию кнопки <<Оплатить>>", keyboard=temp_keyboard.get_json())
    temp_keyboard = Keyboard(inline=True)
    temp_keyboard.add(Callback("Проверить оплату", payload={"command": "check_payment", "billId": payment["billId"]}))
    await message.answer(f"После оплаты, нажмите кнопку <<Проверить оплату>>", keyboard=temp_keyboard.get_json())
    await bp.state_dispenser.set(message.from_id, AddBalance.CHECK)
