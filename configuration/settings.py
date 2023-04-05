from aiogram import Dispatcher
import logging

from aiogram import types
from decouple import config
from handlers.commands import register as reg_handlers
from handlers.superuser import register as reg_superuser
from handlers.bike import register as reg_bike
from handlers.booking import register as reg_booking
# from handlers.test import register as reg_test


bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp: Dispatcher):
    reg_handlers(dp)
    reg_superuser(dp)
    reg_bike(dp)
    reg_booking(dp)
    # reg_test(dp)
