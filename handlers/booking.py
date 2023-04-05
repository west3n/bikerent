import calendar
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_client import add_client, get_client_id
from database.db_bike import get_bike_status
from google_json import sheets
from database.db_booking import add_booking


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


async def back_button(call: types.CallbackQuery, state: FSMContext):
    name = call.from_user.first_name
    await state.finish()
    await call.message.edit_text(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())


async def new_booking_start(call: types.CallbackQuery):
    await call.message.edit_text('Select bike for booking:',
                                 reply_markup=await inline.kb_booking_bike())
    await Booking.bike.set()


async def new_booking_start_step1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['bike'] = call.data.split(":")[1]
    bike_status = await get_bike_status(bike_id=call.data.split(":")[1])
    await call.message.edit_text(f'Bike status: {bike_status[0].capitalize()}\n\nSelect start date:\n\nMonth:',
                                 reply_markup=inline.kb_month())
    await Booking.next()


async def new_booking_start_step2(call: types.CallbackQuery):
    _, month_number = call.data.split("_")
    days_in_month = calendar.monthrange(2023, int(month_number))[1]
    buttons = []
    for day in range(1, days_in_month + 1):
        button = InlineKeyboardButton(str(day), callback_data=f"date_{month_number}_{day}")
        buttons.append(button)
    date_keyboard = InlineKeyboardMarkup(row_width=7)
    date_keyboard.add(*buttons)
    await call.message.edit_text("Select start date:\n\nDay:", reply_markup=date_keyboard)
    await Booking.next()


async def new_booking_start_step3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['start_day'] = call.data
    await call.message.edit_text("Select rental period:", reply_markup=inline.kb_rental_period())
    await Booking.next()


async def new_booking_start_step4(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'other_period':
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
        await call.message.edit_text("Input price after discount:")
        await Booking.next()
    else:
        async with state.proxy() as data:
            data['discount'] = call.data
        await call.message.edit_text("Input client name:")
        await state.set_state(Booking.client_name.state)


async def new_booking_start_step5_2(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['price'] = msg.text
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
    async with state.proxy() as data:
        data['client_contact'] = msg.text
    await add_client(data)
    await msg.answer("New client created!\n\n Please, press button for finish booking",
                     reply_markup=inline.press_x_to_win())
    await Booking.next()


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


async def new_booking_finish(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['delivery_price'] = msg.text
        await add_booking(data)
        await msg.answer(f"Booking saved!")
    else:
        await msg.answer("Use digits only!")


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
    dp.register_message_handler(new_booking_finish, state=Booking.delivery_price)
