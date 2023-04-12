import asyncio
from datetime import timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards import inline
from database import db_admins



async def back_button(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    name = call.from_user.first_name
    tg_id = call.from_user.id
    user_status = await db_admins.check_status(tg_id)
    if user_status:
        if user_status[0] == "superuser":
            await call.message.edit_text(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())
        elif user_status[0] == "manager":
            await call.message.edit_text(f"Hello, manager {name}!", reply_markup=inline.start_manager())
        elif user_status[0] == "deliveryman":
            await call.message.edit_text(f"Hello, deliveryman {name}!", reply_markup=inline.start_deliveryman())


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


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main', state='*')
    dp.register_callback_query_handler(main_information, text='information')
