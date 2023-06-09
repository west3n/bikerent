import io

import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputMediaPhoto
from aiogram.utils.exceptions import BadRequest

from database import db_admins, db_bike, db_service
from database.db_booking import check_booking, get_client_id
from google_json import sheets
from keyboards import inline
from handlers import bike_service
from handlers.qr_generation import generate_qr
from database.db_delivery import add_new_delivery
from database.db_client import update_after_delivery
from database.db_bike import get_millage, update_millage
from database.db_rent import add_new_rent
from database.db_service import db_create_new_task


class Delivery(StatesGroup):
    bike_id = State()
    booking_id = State()
    bike_millage = State()
    leftside_photo = State()
    frontside_photo = State()
    rightside_photo = State()
    backside_photo = State()
    add_photo = State()
    add_photo_2 = State()
    add_photo_3 = State()
    add_photo_4 = State()
    add_photo_5 = State()
    add_photo_6 = State()
    add_photo_7 = State()
    add_photo_8 = State()
    passport_number = State()
    passport_photo = State()
    license_photo = State()
    client_with_passport_photo = State()
    instagram_account = State()
    phone_number = State()
    payment_method = State()
    qr_code = State()
    confirmation = State()
    finish = State()


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


async def confirm_qr(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    name = call.from_user.first_name
    tg_id = call.from_user.id
    user_status = await db_admins.check_status(tg_id)
    if user_status:
        if user_status[0] == "superuser":
            await call.message.answer(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())
        elif user_status[0] == "manager":
            await call.message.answer(f"Hello, manager {name}!", reply_markup=inline.start_manager())
        elif user_status[0] == "deliveryman":
            await call.message.answer(f"Hello, deliveryman {name}!", reply_markup=inline.start_deliveryman())


async def delivery_bike(call: types.CallbackQuery):
    bikes = await db_bike.get_bike_booking_status()
    if not bikes:
        await call.message.edit_text("There's no bookings to deliver!", reply_markup=inline.kb_main_menu())
    else:
        await call.message.edit_text("Select bike:", reply_markup=await inline.kb_all_bookings())
        await Delivery.bike_id.set()


async def delivery_booking(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['bike_id'] = call.data.split(":")[1]
    bookings = await check_booking(data.get('bike_id'))
    if bookings:
        await call.message.edit_text("Select booking:",
                                     reply_markup=await inline.kb_start_delivery(int(data.get("bike_id"))))
        await Delivery.next()
    else:
        await call.message.edit_text("There's no bookings!",
                                     reply_markup=await inline.kb_start_delivery(int(data.get("bike_id"))))


async def delivery_millage(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.finish()
        await call.message.edit_text("Select bike:", reply_markup=await inline.kb_all_bookings())
        await Delivery.bike_id.set()
    else:
        async with state.proxy() as data:
            data['booking_id'] = call.data.split(":")[1]
        millage = await get_millage(bike_id=int(data.get('bike_id')))
        await call.message.edit_text(f"Millage now: {millage}\n\n"
                                     f"Input bike millage:")
        await Delivery.next()


async def delivery_leftside(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():

        async with state.proxy() as data:
            millage = await get_millage(bike_id=int(data.get('bike_id')))
            if int(msg.text) >= millage:
                data["bike_millage"] = msg.text
                await msg.answer("Make photo of LEFT side and send to bot:")
                await Delivery.next()
            else:
                await msg.delete()
                await msg.answer(f"Millage data can't be less than existing equal: {millage}\n"
                                 f"Try again!")

    else:
        await msg.delete()
        await msg.answer("Only digits!")


async def delivery_frontside(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['leftside_photo'] = photo_bytes
    await msg.answer("Make photo of FRONT side and send to bot:")
    await Delivery.next()


async def delivery_rightside(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['frontside_photo'] = photo_bytes
    await msg.answer("Make photo of RIGHT side and send to bot:")
    await Delivery.next()


async def delivery_backside(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['rightside_photo'] = photo_bytes
    await msg.answer("Make photo of BACK side and send to bot:")
    await Delivery.next()


async def delivery_add_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['backside_photo'] = photo_bytes
    await msg.answer("You want to add more photos?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make FIRST additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_2_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make SECOND additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_2'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_3_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make THIRD additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_4(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_3'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_4_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make FOURTH additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_5(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_4'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_5_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make FIFTH additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_6(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_5'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_6_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make SIXTH additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_7(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_6'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_7_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make SEVENTH additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_add_photo_8(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_7'] = photo_bytes
    await msg.answer("You want to add one more photo?", reply_markup=inline.kb_yesno())


async def delivery_add_photo_8_callback_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Make LAST additional photo:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.add_photo_8.state)
        await call.message.edit_text("Input passport number:")
        await Delivery.next()


async def delivery_passport_number(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['add_photo_8'] = photo_bytes
    await msg.answer("Input passport number:")
    await Delivery.next()


async def delivery_passport_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['passport_number'] = msg.text
    await msg.answer("Make photo of PASSPORT and send to bot:")
    await Delivery.next()


async def delivery_license_existing(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['passport_photo'] = photo_bytes
    await msg.answer("Do you want to add LICENSE photo?", reply_markup=inline.kb_yesno())


async def delivery_license_photo(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await call.message.edit_text("Make photo of LICENSE and send to bot:")
        await Delivery.next()
    else:
        await state.set_state(Delivery.license_photo.state)
        await call.message.edit_text("Make photo of CLIENT WITH PASSPORT and send to bot:")
        await Delivery.next()


async def delivery_client_with_passport_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['license_photo'] = photo_bytes
    await msg.answer("Make photo of CLIENT WITH PASSPORT and send to bot:")
    await Delivery.next()


async def delivery_instagram_account(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['client_with_passport_photo'] = photo_bytes
    await msg.answer("You want do add client Instagram account?", reply_markup=inline.kb_yesno())
    await Delivery.next()


async def delivery_instagram_account_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await call.message.edit_text("Input client instagram account:")
        await state.set_state(Delivery.instagram_account.state)
    else:
        await call.message.edit_text("Input client phone number:")
        await state.set_state(Delivery.phone_number.state)


async def delivery_phone_number(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['instagram_account'] = msg.text
    await msg.answer("Input client phone number:")
    await Delivery.next()


async def delivery_payment_method(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = msg.text
    await msg.answer("Select payment method:", reply_markup=inline.kb_payment_method())
    await Delivery.next()


async def delivery_saving_data(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    async with state.proxy() as data:
        data['payment_method'] = call.data.capitalize()
        booking_id = int(data.get('booking_id'))
        await add_new_delivery(data)
        client_id = await get_client_id(booking_id)
        client_id = client_id[0]
        await update_after_delivery(data, client_id)
        img_buffer = await generate_qr(client_id)
        await call.message.bot.send_photo(
            call.message.chat.id,
            photo=img_buffer,
            caption='Show this QR to client',
            reply_markup=inline.kb_confirm_qr())
        await update_millage(int(data.get('bike_millage')), int(data.get('bike_id')))
        # oil_service_data = await db_service.take_data_from_oil_service(int(data.get('bike_id')))
        # oil_need_change = oil_service_data[0]
        # last_oil_change_millage = oil_service_data[1]
        # new_mileage = int(data.get('bike_millage'))
        # await bike_service.check_oil_change(int(data.get('bike_id')), oil_need_change,
        #                                     last_oil_change_millage, new_mileage)
        await add_new_rent(booking_id)
        group_id = decouple.config("GROUP_ID")
        photo_keys = ['leftside_photo', 'rightside_photo', 'frontside_photo', 'backside_photo', 'passport_photo',
                      'license_photo', 'client_with_passport_photo']
        photo_group = []
        for key in photo_keys:
            photo_data = data.get(key)
            if photo_data:
                photo_group.append(InputMediaPhoto(io.BytesIO(photo_data)))
        media_group = await call.bot.send_media_group(chat_id=group_id,
                                                      media=photo_group)

        await call.bot.send_message(chat_id=group_id,
                                    text=f'New delivery:\n\n'
                                         f'Bike ID: {data.get("bike_id")}\n'
                                         f'Client passport: {data.get("passport_number")}\n'
                                         f'Client Instagram: {data.get("instagram_account")}\n'
                                         f'Client Phone: {data.get("phone_number")}\n'
                                         f'Payment method: {data.get("payment_method")}',
                                    reply_to_message_id=media_group[0].message_id)

        if data.get('add_photo'):
            add_photos = []
            add_photo1 = io.BytesIO(data.get('add_photo'))
            add_photos.append(InputMediaPhoto(add_photo1))
            for i in range(2, 9):
                photo_data = data.get(f'add_photo_{i}')
                if photo_data:
                    add_photos.append(InputMediaPhoto(io.BytesIO(photo_data)))

            await call.bot.send_media_group(chat_id=group_id,
                                            media=add_photos)
            bike = await db_bike.get_bike(int(data.get('bike_id')))
            service_id = await db_create_new_task(bike[0], task='Repair_task')
            await sheets.new_task_sheets(service_id, bike[0], "Repair_task")
            await call.bot.send_message(chat_id=group_id,
                                        reply_to_message_id=media_group[0].message_id,
                                        text=f"<b>New SERVICE TASK created:</b>\n\n"
                                             f"Bike ID: {bike[0]} - {bike[1]}, {bike[2]}\n"
                                             f"Task: Repair")

        await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main', state='*')
    dp.register_callback_query_handler(confirm_qr, text='confirm_qr', state='*')
    dp.register_callback_query_handler(delivery_bike, text='delivery')
    dp.register_callback_query_handler(delivery_booking, state=Delivery.bike_id)
    dp.register_callback_query_handler(delivery_millage, state=Delivery.booking_id)
    dp.register_message_handler(delivery_leftside, state=Delivery.bike_millage)
    dp.register_message_handler(delivery_frontside, content_types=['photo'], state=Delivery.leftside_photo)
    dp.register_message_handler(delivery_rightside, content_types=['photo'], state=Delivery.frontside_photo)
    dp.register_message_handler(delivery_backside, content_types=['photo'], state=Delivery.rightside_photo)
    dp.register_message_handler(delivery_add_photo, content_types=['photo'], state=Delivery.backside_photo)
    dp.register_callback_query_handler(delivery_add_photo_callback_handler, state=Delivery.backside_photo)
    dp.register_message_handler(delivery_add_photo_2, content_types=['photo'], state=Delivery.add_photo)
    dp.register_callback_query_handler(delivery_add_photo_2_callback_handler, state=Delivery.add_photo)
    dp.register_message_handler(delivery_add_photo_3, content_types=['photo'], state=Delivery.add_photo_2)
    dp.register_callback_query_handler(delivery_add_photo_3_callback_handler, state=Delivery.add_photo_2)
    dp.register_message_handler(delivery_add_photo_4, content_types=['photo'], state=Delivery.add_photo_3)
    dp.register_callback_query_handler(delivery_add_photo_4_callback_handler, state=Delivery.add_photo_3)
    dp.register_message_handler(delivery_add_photo_5, content_types=['photo'], state=Delivery.add_photo_4)
    dp.register_callback_query_handler(delivery_add_photo_5_callback_handler, state=Delivery.add_photo_4)
    dp.register_message_handler(delivery_add_photo_6, content_types=['photo'], state=Delivery.add_photo_5)
    dp.register_callback_query_handler(delivery_add_photo_6_callback_handler, state=Delivery.add_photo_5)
    dp.register_message_handler(delivery_add_photo_7, content_types=['photo'], state=Delivery.add_photo_6)
    dp.register_callback_query_handler(delivery_add_photo_7_callback_handler, state=Delivery.add_photo_6)
    dp.register_message_handler(delivery_add_photo_8, content_types=['photo'], state=Delivery.add_photo_7)
    dp.register_callback_query_handler(delivery_add_photo_8_callback_handler, state=Delivery.add_photo_7)
    dp.register_message_handler(delivery_passport_number, content_types=['photo'], state=Delivery.add_photo_8)
    dp.register_message_handler(delivery_passport_photo, state=Delivery.passport_number)
    dp.register_message_handler(delivery_license_existing, content_types=['photo'], state=Delivery.passport_photo)
    dp.register_callback_query_handler(delivery_license_photo, state=Delivery.passport_photo)
    dp.register_message_handler(delivery_client_with_passport_photo, content_types=['photo'],
                                state=Delivery.license_photo)
    dp.register_message_handler(delivery_instagram_account, content_types=['photo'],
                                state=Delivery.client_with_passport_photo)
    dp.register_callback_query_handler(delivery_instagram_account_confirm, state=Delivery.instagram_account)
    dp.register_message_handler(delivery_phone_number, state=Delivery.instagram_account)
    dp.register_message_handler(delivery_payment_method, state=Delivery.phone_number)
    dp.register_callback_query_handler(delivery_saving_data, state=Delivery.payment_method)
