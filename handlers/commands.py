from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from database import db_admins
from keyboards import inline


async def bot_start(msg: types.Message):
    await msg.delete()
    name = msg.from_user.first_name
    tg_id = msg.from_user.id
    user_status = await db_admins.check_status(tg_id)
    if user_status:
        if user_status[0] == "superuser":
            await msg.answer(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())
        elif user_status[0] == "manager":
            await msg.answer(f"Hello, manager {name}!", reply_markup=inline.start_manager())
        elif user_status[0] == "deliveryman":
            await msg.answer(f"Hello, deliveryman {name}!", reply_markup=inline.start_deliveryman())
    else:
        await msg.answer(f"Resend this message to @Jivs69:\n\n"
                         f"Telegram ID: {msg.from_id}")


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
