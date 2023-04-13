import logging

from aiogram import types, Dispatcher
from decouple import config

from handlers.commands import register as reg_handlers
from handlers.superuser import register as reg_superuser
from handlers.bike import register as reg_bike
from handlers.booking import register as reg_booking
from handlers.delivery import register as reg_delivery
from handlers.finish_rent import register as reg_finish_rent
from handlers.extend_current_rental import register as reg_extend_current_rental
from handlers.information import register as reg_information
from handlers.bike_service import register as reg_bike_service


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
    reg_delivery(dp)
    reg_finish_rent(dp)
    reg_extend_current_rental(dp)
    reg_information(dp)
    reg_bike_service(dp)
