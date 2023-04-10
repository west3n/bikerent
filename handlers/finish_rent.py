from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database import db_bike, db_rent, db_client
from decouple import config
from keyboards import inline


class FinishRent(StatesGroup):
    rent_id = State()
    extra_cost_confirm = State()
    extra_cost_amount = State()
    extra_cost_comment = State()
    mileage = State()
    repair_comment = State()
    confirm = State()
    finish = State()


async def finish_rent_start(call: types.CallbackQuery):
    rent_list = await db_rent.all_rent()
    if rent_list:
        await call.message.edit_text("Select rent which you want to finish:", reply_markup=await inline.kb_all_rent())
        await FinishRent.rent_id.set()
    else:
        await call.message.edit_text("You have no rents to finish!", reply_markup=inline.kb_main_menu())


async def finish_rent_extra_cost(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["rent_id"] = call.data.split(":")[1]
    await call.message.edit_text("You want to add extra costs for client?", reply_markup=inline.kb_yesno())
    await FinishRent.next()


async def finish_rent_extra_cost_amount(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Input extra costs amount:")
        await FinishRent.next()
    else:
        async with state.proxy() as data:
            await state.set_state(FinishRent.extra_cost_comment.state)
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            millage = await db_bike.get_millage(int(bike_id[0]))
            await call.message.edit_text(f"Current mileage amount: {millage}\n"
                                         f"Input new bike mileage:")
            await FinishRent.next()


async def finish_rent_extra_cost_comment(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data["extra_cost_amount"] = msg.text
            await msg.answer("Input extra costs comment:")
            await FinishRent.next()
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def finish_rent_mileage(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["extra_cost_comment"] = msg.text
        bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
        millage = await db_bike.get_millage(int(bike_id[0]))
        await msg.answer(f"Current mileage amount: {millage}\n"
                         f"Input new bike mileage:")
        await FinishRent.next()


async def finish_rent_repair(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            millage = await db_bike.get_millage(int(bike_id[0]))
            if int(millage) < int(msg.text):
                data["mileage"] = msg.text
                await msg.answer("Bike needs repair?", reply_markup=inline.kb_yesno())
                await FinishRent.next()
            else:
                await msg.delete()
                await msg.answer(f"Mileage data can't be less than existing equal: {millage}\n"
                                 f"Try again!")
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def finish_rent_repair_comment(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await call.message.edit_text("Input comment OR make photo and send it to bot")
        await FinishRent.next()
    else:
        await state.set_state(FinishRent.finish.state)
        async with state.proxy() as data:
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            bike_info = await db_bike.get_more_bike_info(int(bike_id[0]))
            rent_info = await db_rent.get_all_rent_info(int(bike_id[0]))
            client_name = await db_client.get_client_name(int(rent_info[2]))
            print(data)
            await call.message.edit_text(f"Confirm rent finish:\n\n"
                                         f"Bike model: {bike_info[1]} {bike_info[2]}\n"
                                         f"Bike plate number: {bike_info[8]}\n"
                                         f"Client name: {client_name[0]}\n"
                                         f"New mileage: {data.get('mileage')}\n", reply_markup=inline.kb_yesno())


async def client_bot(client_tg, data, client_id):
    bot = Bot(config("CLIENT_BOT_TOKEN"))
    extra_cost = data.get('extra_cost_amount') if data.get('extra_cost_amount') else 0
    comment = data.get('extra_cost_comment') if data.get('extra_cost_comment') else "No comments"
    await bot.send_message(chat_id=client_tg[0],
                           text=f"Your rent finished!\n\n"
                                f"Extra cost: {extra_cost}\n"
                                f"Comment: {comment}")
    await db_client.update_after_finish_rent(client_id)


async def finish_rent_confirm(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text:
            data["repair_comment"] = msg.text
        elif msg.photo:
            file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
            photo_bytes = file.read()
            data["repair_comment"] = photo_bytes
        bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
        bike_info = await db_bike.get_more_bike_info(int(bike_id[0]))
        rent_info = await db_rent.get_all_rent_info(int(bike_id[0]))
        client_name = await db_client.get_client_name(int(rent_info[2]))
        await msg.answer(f"Confirm rent finish:\n\n"
                         f"Bike model: {bike_info[1]} {bike_info[2]}\n"
                         f"Bike plate number: {bike_info[8]}\n"
                         f"Client name: {client_name[0]}\n"
                         f"New mileage: {data.get('mileage')}", reply_markup=inline.kb_yesno())
        await FinishRent.next()


async def finish_rent(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        async with state.proxy() as data:
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            await db_bike.update_millage(int(data.get('mileage')), bike_id[0])
            await call.message.edit_text("You successfully finish rent!", reply_markup=inline.kb_main_menu())
            rent_info = await db_rent.get_all_rent_info(int(bike_id[0]))
            client_tg = await db_client.get_tg_id(int(rent_info[2]))
            client_id = int(rent_info[2])
            await client_bot(client_tg, data, client_id)
            await state.finish()
            await db_rent.finish_rent(int(data.get('rent_id')))
    else:
        await call.message.edit_text("You cancelled rent finishing!", reply_markup=inline.kb_main_menu())
        await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(finish_rent_start, text='finish_rent')
    dp.register_callback_query_handler(finish_rent_extra_cost, state=FinishRent.rent_id)
    dp.register_callback_query_handler(finish_rent_extra_cost_amount, state=FinishRent.extra_cost_confirm)
    dp.register_message_handler(finish_rent_extra_cost_comment, state=FinishRent.extra_cost_amount)
    dp.register_message_handler(finish_rent_mileage, state=FinishRent.extra_cost_comment)
    dp.register_message_handler(finish_rent_repair, state=FinishRent.mileage)
    dp.register_callback_query_handler(finish_rent_repair_comment, state=FinishRent.repair_comment)
    dp.register_message_handler(finish_rent_confirm, content_types=["text", "photo"], state=FinishRent.confirm)
    dp.register_callback_query_handler(finish_rent, state=FinishRent.finish)