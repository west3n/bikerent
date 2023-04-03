from aiogram import Dispatcher, types


async def bot_start(msg: types.Message):
    await msg.delete()
    name = msg.from_user.first_name
    await msg.answer(f"Hello, {name}!")


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
