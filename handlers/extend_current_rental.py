from datetime import timedelta

import decouple
from aiogram import Dispatcher, types, Bot
from decouple import config
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import db_rent, db_bike, db_client
from keyboards import inline
from google_json import sheets


class ExtendRent(StatesGroup):
    rent_id = State()
    rental_period = State()
    rental_period_days = State()
    discount = State()
    payment_method = State()
    confirm = State()
    finish = State()


async def extend_current_rental_start(call: types.CallbackQuery):
    rent_list = await db_rent.all_rent()
    if rent_list:
        await call.message.edit_text("Select rent which you want to extend:", reply_markup=await inline.kb_all_rent())
        await ExtendRent.rent_id.set()
    else:
        await call.message.edit_text("You have no rents to extend!", reply_markup=inline.kb_main_menu())


async def extend_current_rental_period(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["rent_id"] = call.data.split(":")[1]
        await call.message.edit_text("Select rental period:", reply_markup=inline.kb_rental_period())
        await ExtendRent.next()


async def extend_current_rental_days(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.finish()
        await call.message.edit_text("Select rent which you want to extend:", reply_markup=await inline.kb_all_rent())
        await ExtendRent.rent_id.set()
    else:
        async with state.proxy() as data:
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            if call.data == "1_day":
                rental_price = await sheets.coefficient_math(int(bike_id[0]), 1)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(ExtendRent.discount.state)
            elif call.data == "1_week":
                rental_price = await sheets.coefficient_math(int(bike_id[0]), 7)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(ExtendRent.discount.state)
            elif call.data == "1_month":
                rental_price = await sheets.coefficient_math(int(bike_id[0]), 30)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(ExtendRent.discount.state)
            elif call.data == 'other_period':
                await call.message.edit_text("Input rental period amount (DAYS):")
                await ExtendRent.next()


async def extend_current_rental_other_period(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            rental_price = await sheets.coefficient_math(int(bike_id[0]), int(msg.text))
            data.update({'rental_period': msg.text, 'price': rental_price})
            await msg.answer(f"Suggested price is {rental_price}\nApply discount?",
                             reply_markup=inline.kb_yesno())
            await ExtendRent.next()
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def extend_current_rental_discount(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as data:
            await call.message.edit_text(f"Price before discount - {data.get('price')}\n\n"
                                         f"Input price after discount:")
            await ExtendRent.next()
    else:
        await state.set_state(ExtendRent.confirm.state)
        async with state.proxy() as data:
            data['discount'] = 0
        rental_period = data.get('rental_period')
        if not rental_period.isdigit():
            if rental_period == '1_day':
                rental_period = 1
            elif rental_period == '1_week':
                rental_period = 7
            elif rental_period == '1_month':
                rental_period = 30
        bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
        bike_info = await db_bike.get_more_bike_info(int(bike_id[0]))
        rent_info = await db_rent.get_all_rent_info(int(bike_id[0]))
        client_name = await db_client.get_client_name(int(rent_info[2]))
        end_date = await db_rent.gen_end_date(int(data.get("rent_id")))
        new_end_day = (end_date[0] + timedelta(days=int(rental_period)))
        await call.message.edit_text(f"Confirm new rent data:\n\n"
                                     f"Bike model: {bike_info[1]} {bike_info[2]}\n"
                                     f"Bike plate number: {bike_info[8]}\n"
                                     f"Client name: {client_name[0]}\n"
                                     f'New rental end date: {new_end_day.strftime("%d.%m.%Y")}',
                                     reply_markup=inline.kb_yesno())
        await ExtendRent.next()


async def extend_current_rental_confirm(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['discount'] = msg.text
            rental_period = data.get('rental_period')
            if not rental_period.isdigit():
                if rental_period == '1_day':
                    rental_period = 1
                elif rental_period == '1_week':
                    rental_period = 7
                elif rental_period == '1_month':
                    rental_period = 30
            else:
                rental_period = int(data.get('rental_period'))
            bike_id = await db_rent.get_bike_id(int(data.get("rent_id")))
            bike_info = await db_bike.get_more_bike_info(int(bike_id[0]))
            rent_info = await db_rent.get_all_rent_info(int(bike_id[0]))
            client_name = await db_client.get_client_name(int(rent_info[2]))
            end_date = await db_rent.gen_end_date(int(data.get("rent_id")))
            new_end_day = (end_date[0] + timedelta(days=int(rental_period)))
            await msg.answer(f"Confirm new rent data:\n\n"
                             f"Bike model: {bike_info[1]} {bike_info[2]}\n"
                             f"Bike plate number: {bike_info[8]}\n"
                             f"Client name: {client_name[0]}\n"
                             f'New rental end date: {new_end_day.strftime("%d.%m.%Y")}',
                             reply_markup=inline.kb_yesno())
            await ExtendRent.next()
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def client_bot(client_tg, new_end_day):
    bot = Bot(config("CLIENT_BOT_TOKEN"))
    await bot.send_message(chat_id=client_tg[0],
                           text=f"Your rent has been update: \n"
                                f'New rental end date: {new_end_day.strftime("%d.%m.%Y")}')


async def extend_current_rental_finish(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == "yes":
            rental_period = data.get('rental_period')
            if not rental_period.isdigit():
                if rental_period == '1_day':
                    rental_period = 1
                elif rental_period == '1_week':
                    rental_period = 7
                elif rental_period == '1_month':
                    rental_period = 30
            else:
                rental_period = int(data.get('rental_period'))
            end_date = await db_rent.gen_end_date(int(data.get("rent_id")))
            new_end_day = (end_date[0] + timedelta(days=rental_period))
            await db_rent.update_date(int(data.get('rent_id')), new_end_day)
            client_id = await db_rent.get_client_id(int(data.get('rent_id')))
            client_tg = await db_client.get_tg_id(client_id)
            group_id = decouple.config("GROUP_ID")
            await client_bot(client_tg, new_end_day)
            await call.message.edit_text("You successfully extend rental!", reply_markup=inline.kb_main_menu())
            await state.finish()
        else:
            await call.message.edit_text("You cancelled rent extending!", reply_markup=inline.kb_main_menu())
            await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(extend_current_rental_start, text='extend_current_rental')
    dp.register_callback_query_handler(extend_current_rental_period, state=ExtendRent.rent_id)
    dp.register_callback_query_handler(extend_current_rental_days, state=ExtendRent.rental_period)
    dp.register_message_handler(extend_current_rental_other_period, state=ExtendRent.rental_period_days)
    dp.register_callback_query_handler(extend_current_rental_discount, state=ExtendRent.discount)
    dp.register_message_handler(extend_current_rental_confirm, state=ExtendRent.confirm)
    dp.register_callback_query_handler(extend_current_rental_finish, state=ExtendRent.finish)
