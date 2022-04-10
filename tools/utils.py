from functools import wraps

from vkbottle import Bot
from vkbottle.bot import Message

from config import bot_token

bot = Bot(bot_token)


async def putUser(link: str) -> int:
    if link.isdigit():
        return int(link)
    if link.startswith('[') and link.endswith(']'):
        return (
            await bot.api.utils.resolve_screen_name(screen_name=link.split('|')[0][1:])).object_id
    if "vk.com/" in link:
        return (
            await bot.api.utils.resolve_screen_name(screen_name=link.split("vk.com/")[-1])).object_id
    return (
        await bot.api.utils.resolve_screen_name(screen_name=link)).object_id


async def getName(uid: int, name_case: str = "nom") -> tuple[str, str]:
    if uid < 0:
        group_data = (await bot.api.groups.get_by_id(group_ids=[str(-uid)]))[0]
        return "Сообщество", f"<<{group_data.name}>>"
    userData = await bot.api.users.get(user_ids=[str(uid)], name_case=name_case)
    return userData[0].first_name, userData[0].last_name


def check_role(priority):
    from db.models import User
    from modules.privatemessage import start

    def decorator(func):
        @wraps(func)
        async def checker(message: Message, *args, **kwargs):
            user_account = User.objects.get_or_create(user_id=message.from_id)[0]
            if user_account.role.priority >= priority:
                return await func(message, *args, **kwargs)
            else:
                return await start(message)

        return checker

    return decorator
