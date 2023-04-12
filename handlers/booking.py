import calendar
import re
from datetime import timedelta, datetime, date

import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import db_admins, postgresql
from keyboards import inline
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_client import add_client, get_client_id
from database.db_bike import get_bike_status, change_bike_status_to_booking, change_bike_status_to_free
from google_json import sheets
from database.db_booking import add_booking, check_booking, delete_booking
from database.db_rent import get_all_rent


class Booking(StatesGroup):
    bike = State()
    start_month = State()
    start_day = State()
    rental_period = State()
    rental_period_days = State()
    discount = State()
    price = State()
    client_name = State()
    client_contact = State()
    client_id = State()
    address = State()
    delivery_time = State()
    delivery_price = State()
    booking_comment = State()
    send_to_group = State()


class CancelBooking(StatesGroup):
    bike = State()
    confirm = State()
    finish = State()


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


async def new_booking_start(call: types.CallbackQuery):
    await call.message.edit_text('Select bike for booking:',
                                 reply_markup=await inline.kb_booking_bike())
    await Booking.bike.set()


async def new_booking_start_step1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['bike'] = call.data.split(":")[1]
    bike_status = await get_bike_status(bike_id=call.data.split(":")[1])
    if bike_status[0] == 'booking':
        bookings = await check_booking(bike_id=data.get('bike'))
        if bookings:
            x = '<b>Booking</b>\n'
            for booking in bookings:
                start_date = booking[2].strftime("%d.%m.%Y")
                end_date = (booking[2] + timedelta(days=int(booking[3]))).strftime("%d.%m.%Y")
                x += f'ID: {booking[0]} - Start: {start_date}, End: {end_date}\n'

            await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n'
                                         f'{x}\n'
                                         f'\nSelect start date:\n\nMonth:',
                                         reply_markup=inline.kb_month())
        else:
            await change_bike_status_to_free(bike_id=data.get('bike'))
            await call.message.edit_text(f'Bike status: Free\n'
                                         f'\nSelect start date:\n\nMonth:',
                                         reply_markup=inline.kb_month())
    if bike_status[0] == 'rent':
        bookings = await check_booking(bike_id=data.get('bike'))
        rents = await get_all_rent(bike_id=data.get('bike'))
        if bookings != [] and rents != []:
            x = '<b>Booking</b>\n'
            for booking in bookings:
                start_date = booking[2].strftime("%d.%m.%Y")
                end_date = (booking[2] + timedelta(days=int(booking[3]))).strftime("%d.%m.%Y")
                x += f'ID: {booking[0]} - Start: {start_date}, End: {end_date}\n'
            y = '<b>Rent</b>\n'
            for rent in rents:
                start_date = rent[3].strftime("%d.%m.%Y")
                end_date = rent[4].strftime("%d.%m.%Y")
                y += f"ID: {rent[0]} - Start: {start_date}, End: {end_date}"

            await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n'
                                         f'{x}\n'
                                         f'{y}\n'
                                         f'\nSelect start date:\n\nMonth:',
                                         reply_markup=inline.kb_month())
        else:
            if rents:
                y = '<b>Rent</b>\n'
                for rent in rents:
                    start_date = rent[3].strftime("%d.%m.%Y")
                    end_date = rent[4].strftime("%d.%m.%Y")
                    y += f"ID: {rent[0]} - Start: {start_date}, End: {end_date}"
                await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n'
                                             f'{y}\n'
                                             f'\nSelect start date:\n\nMonth:',
                                             reply_markup=inline.kb_month())
            if bookings:
                x = '<b>Booking</b>\n'
                for booking in bookings:
                    start_date = booking[2].strftime("%d.%m.%Y")
                    end_date = (booking[2] + timedelta(days=int(booking[3]))).strftime("%d.%m.%Y")
                    x += f'ID: {booking[0]} - Start: {start_date}, End: {end_date}\n'
                await change_bike_status_to_booking(data.get('bike'))
                await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n'
                                             f'{x}\n'
                                             f'\nSelect start date:\n\nMonth:',
                                             reply_markup=inline.kb_month())
            else:
                await change_bike_status_to_free(bike_id=data.get('bike'))
                await call.message.edit_text(f'Bike status: Free\n'
                                             f'\nSelect start date:\n\nMonth:',
                                             reply_markup=inline.kb_month())
    else:
        await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n\nSelect start date:\n\nMonth:',
                                     reply_markup=inline.kb_month())

    await Booking.next()


async def new_booking_start_step2(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.finish()
        await call.message.edit_text('Select bike for booking:',
                                     reply_markup=await inline.kb_booking_bike())
        await Booking.bike.set()
    else:
        async with state.proxy() as data:
            data["start_month"] = call.data
            _, month_number = call.data.split("_")
            days_in_month = calendar.monthrange(2023, int(month_number))[1]
            buttons = []
            for day in range(1, days_in_month + 1):
                button = InlineKeyboardButton(str(day), callback_data=f"date_{month_number}_{day}")
                buttons.append(button)
            date_keyboard = InlineKeyboardMarkup(row_width=7)
            date_keyboard.add(*buttons)
            previous_step = InlineKeyboardButton("Back", callback_data="back")
            date_keyboard.add(previous_step)
            await call.message.edit_text("Select start date:\n\nDay:", reply_markup=date_keyboard)
            await Booking.next()


async def new_booking_start_step3(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.set_state(Booking.bike.state)
        async with state.proxy() as data:
            bike_status = await get_bike_status(bike_id=int(data.get('bike')))
            await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n\nSelect start date:\n\nMonth:',
                                         reply_markup=inline.kb_month())
            await Booking.next()
    else:
        async with state.proxy() as data:
            data['start_day'] = call.data
        await call.message.edit_text("Select rental period:", reply_markup=inline.kb_rental_period())
        await Booking.next()


async def new_booking_start_step4(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.set_state(Booking.start_month.state)
        async with state.proxy() as data:
            _, month_number = data.get('start_month').split("_")
            days_in_month = calendar.monthrange(2023, int(month_number))[1]
            buttons = []
            for day in range(1, days_in_month + 1):
                button = InlineKeyboardButton(str(day), callback_data=f"date_{month_number}_{day}")
                buttons.append(button)
            date_keyboard = InlineKeyboardMarkup(row_width=7)
            date_keyboard.add(*buttons)
            previous_step = InlineKeyboardButton("Back", callback_data="back")
            date_keyboard.add(previous_step)
            await call.message.edit_text("Select start date:\n\nDay:", reply_markup=date_keyboard)
            await Booking.next()
    elif call.data == 'other_period':
        await call.message.edit_text("Input rental period amount (DAYS):")
        await Booking.next()
    else:
        async with state.proxy() as data:
            if call.data == "1_day":
                rental_price = await sheets.coefficient_math(data.get('bike'), 1)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(Booking.discount.state)
            elif call.data == "1_week":
                rental_price = await sheets.coefficient_math(data.get('bike'), 7)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(Booking.discount.state)
            elif call.data == "1_month":
                rental_price = await sheets.coefficient_math(data.get('bike'), 30)
                data.update({'rental_period': call.data, 'price': rental_price})
                await call.message.edit_text(f"Suggested price is {rental_price}\nApply discount?",
                                             reply_markup=inline.kb_yesno())
                await state.set_state(Booking.discount.state)


async def new_booking_start_step4_2(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            rental_price = await sheets.coefficient_math(data.get('bike'), int(msg.text))
            data.update({'rental_period': msg.text, 'price': rental_price})
        await msg.answer(f"Suggested price is {rental_price}\nApply discount?",
                         reply_markup=inline.kb_yesno())
        await Booking.next()
    else:
        await msg.answer("Use digits only!")


async def new_booking_start_step5(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as data:
            await call.message.edit_text(f"Price before discount - {data.get('price')}\n\n"
                                         f"Input price after discount:")
            await Booking.next()
    else:
        async with state.proxy() as data:
            data['discount'] = 0
        await call.message.edit_text("Input client name:")
        await state.set_state(Booking.client_name.state)


async def new_booking_start_step5_2(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            last = int(data.get('price'))
            now = int(msg.text)
            discount = last - now
            data.update({'price': msg.text, 'discount': discount})
            await msg.answer("Input client name:")
            await Booking.next()
    else:
        await msg.answer("Use digits only!")


async def new_booking_start_step6(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['client_name'] = msg.text
    await msg.answer("Input client contact:")
    await Booking.next()


async def new_booking_start_step7(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['client_contact'] = msg.text
        await add_client(data)
        await msg.answer("New client created!\n\n Please, press button for finish booking",
                         reply_markup=inline.press_x_to_win())
        await Booking.next()
    except:
        postgresql.db.rollback()
        await msg.delete()
        await msg.answer("This client already has opened rental! Try again")


async def new_booking_start_step8(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        client_id = await get_client_id(data)
        data['client_id'] = client_id[0]
    await call.message.edit_text('Input address for deliveryman:')
    await Booking.next()


async def new_booking_start_step9(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = msg.text
    await msg.answer('Input TIME for deliveryman:\n\n(ex. 9:30 or 16:00)')
    await Booking.next()


def check_time_format(message):
    pattern = r'^\d{1,2}:\d{2}$'
    if re.match(pattern, message):
        return True
    else:
        return False


async def new_booking_start_step10(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['delivery_time'] = msg.text
        if check_time_format(msg.text):
            await msg.answer('Input delivery price:\n\nIf free delivery - send 0')
            await Booking.next()
        else:
            await msg.delete()
            await msg.answer("Please, use correct template (ex. 9:30 or 16:00)")


async def new_booking_comment(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['delivery_price'] = msg.text
            await msg.answer('You want to add comment to deliveryman?', reply_markup=inline.kb_yesno())
            await Booking.next()
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def new_booking_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await state.set_state(Booking.delivery_price.state)
        await call.message.edit_text("Input comment:")
        await Booking.next()
    else:
        await state.set_state(Booking.booking_comment.state)
        async with state.proxy() as data:
            await add_booking(data)
            await call.message.edit_text(f"Booking saved!", reply_markup=inline.kb_main_menu())
            await change_bike_status_to_booking(bike_id=data.get('bike'))
            await state.finish()


async def new_booking_finish_with_comment(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["booking_comment"] = msg.text
        await add_booking(data)
        await msg.answer(f"Booking saved!", reply_markup=inline.kb_main_menu())
        await change_bike_status_to_booking(bike_id=data.get('bike'))
        await state.finish()


async def new_booking_send_to_group(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        async with state.proxy() as data:
            await add_booking(data)
            group_id = decouple.config("GROUP_ID")
            bike_status = await get_bike_status(bike_id=data.get('bike'))
            if bike_status[0] == 'free':
                await change_bike_status_to_booking(bike_id=data.get('bike'))
            date_str = data.get('start_day')
            date_parts = date_str.split('_')[1:]
            year = datetime.now().year
            month, day = map(int, date_parts)
            date_obj = date(year, month, day)
            delivery_time = data.get('delivery_time')
            time_obj = datetime.strptime(delivery_time, '%H:%M').time()
            datetime_obj = datetime.combine(date_obj, time_obj)
            formatted_datetime = datetime_obj.strftime('%d.%m.%Y %H:%M')
            rental_period = data.get("rental_period")
            if rental_period == "1_day":
                rent_period = 1
            elif rental_period == '1_week':
                rent_period = 7
            elif rental_period == "1_month":
                rent_period = 30
            else:
                rent_period = data.get('rental_period')
            await call.bot.send_message(chat_id=group_id,
                                        text=f"Hello managers! Please make new delivery:\n\n"
                                             f"Client: {data.get('client_name')}, {data.get('client_contact')}\n"
                                             f"Address: {data.get('address')}\n"
                                             f"Delivery date: {formatted_datetime}\n"
                                             f"Rent period: {rent_period} days\n"
                                             f"Rent price: {data.get('price')}\n"
                                             f"Delivery price: {data.get('delivery_price')}\n"
                                             f"Comment for deliveryman: {data.get('booking_comment')}")
            await call.message.edit_text("Booking successfully saved and sent to group!",
                                         reply_markup=inline.kb_main_menu())
            await state.finish()
    else:
        await call.message.edit_text("You cancelled new booking confirmation!",
                                     reply_markup=inline.kb_main_menu())
        await state.finish()


async def cancel_booking(call: types.CallbackQuery):
    await call.message.edit_text("Select bike for cancellation:", reply_markup=await inline.kb_booking_bike())
    await CancelBooking.bike.set()


async def cancel_booking_selection(call: types.CallbackQuery, state: FSMContext):
    bike_id = call.data.split(":")[1]
    async with state.proxy() as data:
        data['bike'] = bike_id
    bookings = await check_booking(bike_id)
    if bookings:
        await call.message.edit_text("Select booking for cancellation:",
                                     reply_markup=await inline.kb_cancel_booking(bike_id))
        await CancelBooking.next()
    else:
        await call.message.edit_text("There's no bookings for cancellation!",
                                     reply_markup=await inline.kb_cancel_booking(bike_id))


async def cancel_booking_confirmation(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.finish()
        await call.message.edit_text("Select bike for cancellation:", reply_markup=await inline.kb_booking_bike())
        await CancelBooking.bike.set()
    else:
        async with state.proxy() as data:
            data['confirm'] = call.data.split(":")[1]
        await call.message.edit_text("Are you sure?",
                                     reply_markup=inline.kb_yesno())
        await CancelBooking.next()


async def cancel_booking_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        async with state.proxy() as data:
            await call.message.edit_text("Booking successfully deleted!", reply_markup=inline.kb_main_menu())
            await delete_booking(int(data.get('confirm')))
            await state.finish()
    else:
        async with state.proxy() as data:
            await state.set_state(CancelBooking.bike.state)
            bike_id = data.get('bike')
            await call.message.edit_text("Select booking for cancellation:",
                                         reply_markup=await inline.kb_cancel_booking(bike_id))
            await CancelBooking.next()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main', state='*')
    dp.register_callback_query_handler(new_booking_start, text="new_booking")
    dp.register_callback_query_handler(new_booking_start_step1, state=Booking.bike)
    dp.register_callback_query_handler(new_booking_start_step2, state=Booking.start_month)
    dp.register_callback_query_handler(new_booking_start_step3, state=Booking.start_day)
    dp.register_callback_query_handler(new_booking_start_step4, state=Booking.rental_period)
    dp.register_message_handler(new_booking_start_step4_2, state=Booking.rental_period_days)
    dp.register_callback_query_handler(new_booking_start_step5, state=Booking.discount)
    dp.register_message_handler(new_booking_start_step5_2, state=Booking.price)
    dp.register_message_handler(new_booking_start_step6, state=Booking.client_name)
    dp.register_message_handler(new_booking_start_step7, state=Booking.client_contact)
    dp.register_callback_query_handler(new_booking_start_step8, state=Booking.client_id)
    dp.register_message_handler(new_booking_start_step9, state=Booking.address)
    dp.register_message_handler(new_booking_start_step10, state=Booking.delivery_time)
    dp.register_message_handler(new_booking_comment, state=Booking.delivery_price)
    dp.register_callback_query_handler(new_booking_finish, state=Booking.booking_comment)
    dp.register_message_handler(new_booking_finish_with_comment, state=Booking.booking_comment)
    dp.register_callback_query_handler(new_booking_send_to_group, state=Booking.send_to_group)
    dp.register_callback_query_handler(cancel_booking, text='cancel_booking')
    dp.register_callback_query_handler(cancel_booking_selection, state=CancelBooking.bike)
    dp.register_callback_query_handler(cancel_booking_confirmation, state=CancelBooking.confirm)
    dp.register_callback_query_handler(cancel_booking_finish, state=CancelBooking.finish)
