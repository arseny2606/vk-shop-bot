import asyncio
import logging
import platform
import sys
import time
import traceback
from datetime import datetime

import nest_asyncio
import psutil

from config import bot_token

sys.dont_write_bytecode = True
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
import django
from vkbottle import Bot, load_blueprints_from_package
from vkbottle.bot import Message

django.setup()
logging.basicConfig(level=logging.ERROR, filename="error.log")

starttime = datetime.now().timestamp()
bot = Bot(bot_token)
print("Инициализирована сессия бота")


async def aEval(code: str) -> str:
    try:
        exec(
            f'async def __ex(): ' +
            ''.join(f'\n {line}' for line in code.split('\n'))
        )
        response = "async function done"
        await locals()['__ex']()
    except:
        response = traceback.format_exc()
    return response


@bot.on.message(text="/пинг")
async def info(message: Message):
    if message.from_id in [309253224]:
        return f"⚙ Понг!\nDate offset: {round(time.time() * 100 - message.date * 100)}ms"


@bot.on.message(text="eval <args>")
async def evalHandler(message: Message, args: str):
    if message.from_id == 309253224:
        if "await" in message.text:
            await message.answer(await aEval(args))
        else:
            try:
                response = eval(args)
            except:
                response = traceback.format_exc()
            await message.answer(response)


@bot.on.message(text="/info")
async def infoHandler(message: Message):
    if message.from_id == 309253224:
        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024 ** 3)
        available_memory = memory.available / (1024 ** 3)
        used_memory = memory.used / (1024 ** 3)
        free_memory = memory.free / (1024 ** 3)

        disk_memory = psutil.disk_usage("/")
        total_disk = disk_memory.total / (1024 ** 3)
        used_disk = disk_memory.used / (1024 ** 3)
        free_disk = disk_memory.free / (1024 ** 3)

        message = f"🖥 Платформа: {platform.platform()}\n💽 ОЗУ:\n  Всего: {total_memory:.3}GB\n  " \
                  f"Не используется: {available_memory:.3}GB\n  Использовано: {used_memory:.3}GB ({memory.percent}%)\n  " \
                  f"Доступно: {free_memory:.3}GB\n📀 Диск:\n  Всего: {total_disk:.4}GB\n  Использовано: " \
                  f"{used_disk:.4}GB ({disk_memory.percent}%)\n  Доступно: {free_disk:.4}GB\n" \
                  f"💿 Нагрузка ЦП: {psutil.cpu_percent()}%"
        return message


@bot.on.message(text="!del")
async def deleteHandler(message: Message):
    if message.from_id == 309253224:
        if message.reply_message is not None:
            await message.ctx_api.messages.delete(
                conversation_message_ids=[message.reply_message.conversation_message_id],
                peer_id=message.peer_id, delete_for_all=True)
        if message.fwd_messages:
            for i in message.fwd_messages:
                try:
                    await message.ctx_api.messages.delete(
                        conversation_message_ids=[i.conversation_message_id],
                        peer_id=message.peer_id, delete_for_all=True)
                except Exception:
                    continue
        try:
            await message.ctx_api.messages.delete(
                conversation_message_ids=[message.conversation_message_id], peer_id=message.peer_id,
                delete_for_all=True)
        except Exception:
            pass


@bot.on.message(text="!peerid")
async def peeridHandler(message: Message):
    if message.from_id in [309253224]:
        return str(message.peer_id)


for bp in load_blueprints_from_package("modules"):
    bp.load(bot)

print("Инициализированы модули бота")


async def handleError(_):
    pass


bot.error_handler.register_error_handler(KeyError, handleError)
bot.error_handler.register_error_handler(KeyboardInterrupt, handleError)


async def main():
    global starttime
    f1 = loop.create_task(bot.run_polling())
    endtime = datetime.now().timestamp()
    print(f"Все сессии инициализированы за {round(endtime - starttime, 2)} секунд.")
    await asyncio.wait([f1])


loop = asyncio.get_event_loop()
nest_asyncio.apply()
loop.run_until_complete(main())
loop.close()
