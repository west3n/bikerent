import asyncio
import io
from datetime import timedelta

from aiogram.utils.exceptions import BadRequest
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards import inline
from database import db_admins, db_bike, db_rent, db_client, db_booking
from google_json import sheets


async def back_button(call: types.CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        name = call.from_user.first_name
        tg_id = call.from_user.id
        user_status = await db_admins.check_status(tg_id)
        if user_status:
            if user_status[0] == "superuser":
                await call.message.edit_text(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())
            elif user_status[0] == "supervisor":
                await call.message.edit_text(f"Hello, supervisor {name}!", reply_markup=inline.start_manager())
            elif user_status[0] == "manager":
                await call.message.edit_text(f"Hello, manager {name}!", reply_markup=inline.start_deliveryman())
    except BadRequest:
        await state.finish()
        name = call.from_user.first_name
        tg_id = call.from_user.id
        user_status = await db_admins.check_status(tg_id)
        if user_status:
            if user_status[0] == "superuser":
                await call.message.delete()
                await call.message.answer(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())
            elif user_status[0] == "supervisor":
                await call.message.delete()
                await call.message.answer(f"Hello, supervisor {name}!", reply_markup=inline.start_manager())
            elif user_status[0] == "manager":
                await call.message.delete()
                await call.message.answer(f"Hello, manager {name}!", reply_markup=inline.start_deliveryman())


async def all_bikes(call: types.CallbackQuery):
    await call.message.edit_text("Select bike for check its price:", reply_markup=await inline.kb_delete_bike())


async def bike_prices(call: types.CallbackQuery):
    await call.message.edit_text('Read data from Google sheets, please wait...')
    await asyncio.sleep(2)
    bike_id = int(call.data.split(":")[1])
    day_price = await sheets.coefficient_math(bike_id, 1)
    week_price = await sheets.coefficient_math(bike_id, 7)
    month_price = await sheets.coefficient_math(bike_id, 30)
    bike_str = "<b>Bike price:</b>\n"
    bike_str += f'Day price: {day_price}\nWeek price: {week_price}\nMonth price: {month_price}'
    await call.message.edit_text(f'{bike_str}', reply_markup=inline.kb_info_back_2())


async def main_information(call: types.CallbackQuery):
    await call.message.edit_text("Select option:", reply_markup=inline.kb_information())


async def free_bikes(call: types.CallbackQuery):
    bikes = await db_bike.get_bike_free_status()
    bike_str = '<b>Free bikes:</b>\n'
    if bikes:
        for bike in bikes:
            bike_str += f'Bike ID: {bike[0]}, Model: {bike[1]}, Plate No: {bike[2]}\n'
    else:
        bike_str = f'No free bikes!'
    await call.message.edit_text(f'{bike_str}', reply_markup=inline.kb_info_back_1())


async def rent_booking_bikes(call: types.CallbackQuery):
    await call.message.edit_text("Select one status:", reply_markup=inline.booking_rent())


async def booking_bikes(call: types.CallbackQuery):
    bookings = await db_booking.all_bookings()
    if bookings:
        booking_str = '<b>Booking bikes:</b>\n'
        for booking in bookings:
            bike = await db_bike.get_bike(booking[1])
            client_name = await db_client.get_client_name(booking[5])
            booking_finish = (booking[2] + timedelta(days=booking[3])).strftime("%d.%m.%Y")
            booking_str += f'<b>Bike ID: {bike[0]}, Model: {bike[1]}, Plate No: {bike[2]}</b>\n'
            booking_str += f'Start: {booking[2].strftime("%d.%m.%Y")}, Finish: {booking_finish}, ' \
                           f'Client Name: {client_name[0]}\n\n'
    else:
        booking_str = "No bookings"
    await call.message.edit_text(f'{booking_str}', reply_markup=inline.kb_info_back())


async def rent_bikes(call: types.CallbackQuery):
    rents = await db_rent.all_rent()
    if rents:
        rent_str = '<b>Rent bikes:</b>\n'
        for rent in rents:
            bike = await db_bike.get_bike(rent[1])
            client_name = await db_client.get_client_name(rent[2])
            rent_str += f'<b>Bike ID: {bike[0]}, Model: {bike[1]}, Plate No: {bike[2]}</b>\n'
            rent_str += f'Start: {rent[3]}, Finish: {rent[4]}, Client Name: {client_name[0]}\n\n'
    else:
        rent_str = "No rentals"
    await call.message.edit_text(f'{rent_str}', reply_markup=inline.kb_info_back())


async def create_new_post(call: types.CallbackQuery):
    await call.message.edit_text("Select bike for upload its description:",
                                 reply_markup=await inline.kb_description_bike())


async def get_description(call: types.CallbackQuery):
    bike_id = int(call.data.split(":")[1])
    bike_photo = await db_bike.get_photo(bike_id)
    photo_io = io.BytesIO(bike_photo[0])
    description = await db_bike.get_bike_description(bike_id)
    await call.message.answer_photo(photo_io, description[0], reply_markup=inline.kb_main_menu())


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main', state='*')
    dp.register_callback_query_handler(main_information,
                                       text=['information', 'info_back_1', 'back', 'back_description'])
    dp.register_callback_query_handler(all_bikes, text=['check_bike_price', 'info_back_2'])
    dp.register_callback_query_handler(bike_prices, lambda c: c.data.startswith('delete_bike'))
    dp.register_callback_query_handler(free_bikes, text='check_available_bikes')
    dp.register_callback_query_handler(rent_booking_bikes, text=['check_rental_status', 'info_back'])
    dp.register_callback_query_handler(booking_bikes, text='info_booking')
    dp.register_callback_query_handler(rent_bikes, text="info_rent")
    dp.register_callback_query_handler(create_new_post, text="create_new_post")
    dp.register_callback_query_handler(get_description, lambda c: c.data.startswith("description"))
