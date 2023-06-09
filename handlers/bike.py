import io

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BadRequest

from keyboards import inline
from database.db_bike import create_new_bike, delete_bike, get_photo, db_update_bike, get_more_bike_info, \
    new_description
from database import db_service, db_admins
from google_json import sheets


class NewBike(StatesGroup):
    brand = State()
    model = State()
    year = State()
    purchase_price = State()
    millage = State()
    abs_cbs = State()
    keyless = State()
    plate_no = State()
    color = State()
    gps = State()
    style = State()
    docs = State()
    exhaust = State()
    photo = State()
    status = State()
    another_one = State()


class DeleteBike(StatesGroup):
    pick = State()
    confirm = State()
    another_one = State()


class UpdateBike(StatesGroup):
    pick = State()
    bike_id = State()
    parameter = State()
    new_parameter = State()


class BikeDescription(StatesGroup):
    bike_id = State()
    title = State()
    power = State()
    description = State()
    other = State()
    confirm = State()


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


async def bike_settings(call: types.CallbackQuery):
    await call.message.edit_text("Select one option:", reply_markup=inline.kb_bike_settings())


async def add_new_bike_step1(call: types.CallbackQuery):
    await call.message.edit_text("Input bike brand:")
    await NewBike.brand.set()


async def add_new_bike_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['brand'] = msg.text
    await msg.answer("Input bike model:")
    await NewBike.next()


async def add_new_bike_step3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['model'] = msg.text
    await msg.answer("Input bike year:")
    await NewBike.next()


async def add_new_bike_step3_v1(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['year'] = msg.text
        await msg.answer("Input bike purchase price:")
        await NewBike.next()
    else:
        await msg.delete()
        await msg.answer("Use digits only!")


async def add_new_bike_step4(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text.isdigit():
            data['purchase_price'] = msg.text
            await msg.answer("Input bike millage:")
            await NewBike.next()
        else:
            await msg.delete()
            await msg.answer("Use digits only!")


async def add_new_bike_step5(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text.isdigit():
            data['millage'] = msg.text
            await msg.answer("Bike has ABS/CBS?", reply_markup=inline.kb_yesno())
            await NewBike.next()
        else:
            await msg.delete()
            await msg.answer("Use digits only!")


async def add_new_bike_step6(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['abs_cbs'] = call.data
    await call.message.edit_text("Bike keyless?", reply_markup=inline.kb_yesno())
    await NewBike.next()


async def add_new_bike_step7(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['keyless'] = call.data
    await call.message.edit_text(f"Input bike plate number:\n"
                                 f"(max: 15 symbols)")
    await NewBike.next()


async def add_new_bike_step8(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if len(msg.text) < 15:
            data['plate_no'] = msg.text
            await msg.answer("Basic or custom color?", reply_markup=inline.kb_basic_custom())
            await NewBike.next()
        else:
            await msg.delete()
            await msg.answer("15 symbols maximum!")


async def add_new_bike_step9(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['color'] = call.data
    await call.message.edit_text("Bike has GPS?", reply_markup=inline.kb_yesno())
    await NewBike.next()


async def add_new_bike_step10(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['gps'] = call.data
    await call.message.edit_text("Select bike style", reply_markup=inline.kb_bike_style())
    await NewBike.next()


async def add_new_bike_step10_v1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['style'] = call.data
    await call.message.edit_text("Bike has documents?", reply_markup=inline.kb_yesno())
    await NewBike.next()


async def add_new_bike_step11(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['docs'] = call.data
    await call.message.edit_text("Select type exhaust:", reply_markup=inline.kb_bike_style())
    await NewBike.next()


async def add_new_bike_step11_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exhaust'] = call.data
    await call.message.edit_text("Send one image of bike")
    await NewBike.next()


async def add_new_bike_step12(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
        photo_bytes = file.read()
        data['photo'] = photo_bytes
    await msg.answer("Select bike status", reply_markup=inline.kb_bike_status())
    await NewBike.next()


async def add_new_bike_finish(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Addition in progress...")
    async with state.proxy() as data:
        data['status'] = call.data
    bike_id = await create_new_bike(data)
    await sheets.new_bike_sheets(data, bike_id)
    await db_service.insert_oil_service_table(bike_id)
    await call.message.edit_text("New bike data successfully saved!\n\nDo you want to add another bike?",
                                 reply_markup=inline.kb_yesno())
    await NewBike.next()


async def add_new_another_bike(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await state.finish()
        await call.message.edit_text("Input bike brand:")
        await NewBike.brand.set()
    else:
        await state.finish()
        name = call.from_user.first_name
        await call.message.edit_text(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())


async def delete_bike_(call: types.CallbackQuery):
    await call.message.edit_text("Select bike which you want to delete:", reply_markup=await inline.kb_delete_bike())
    await DeleteBike.pick.set()


async def delete_confirmation(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.finish()
        await call.message.edit_text("Select one option:", reply_markup=inline.kb_bike_settings())
    else:
        async with state.proxy() as data:
            data['pick'] = call.data
        await call.message.edit_text("Are you sure?", reply_markup=inline.kb_yesno())
        await DeleteBike.next()


async def delete_processing(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        await call.message.edit_text("Deletion in progress...")
        async with state.proxy() as data:
            bike_id = data.get('pick').split(":")[1]
            await delete_bike(int(bike_id))
            await sheets.delete_bike_sheets(bike_id)
            await call.message.edit_text(f"Bike {bike_id} successfully deleted.\n\nYou want to delete another one?",
                                         reply_markup=inline.kb_yesno())
            await DeleteBike.next()
    else:
        await state.set_state(DeleteBike.pick.state)
        await call.message.edit_text("Select bike which you want to delete:",
                                     reply_markup=await inline.kb_delete_bike())
        await DeleteBike.pick.set()


async def delete_another_one(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await state.finish()
        await call.message.edit_text("Select bike which you want to delete:",
                                     reply_markup=await inline.kb_delete_bike())
        await DeleteBike.pick.set()
    else:
        await state.finish()
        name = call.from_user.first_name
        await call.message.edit_text(f"Hello, superuser {name}!", reply_markup=inline.start_superuser())


async def update_bike(call: types.CallbackQuery):
    await call.message.edit_text("Select bike for update:", reply_markup=await inline.kb_update_bike())
    await UpdateBike.pick.set()


async def update_bike_step2(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.finish()
        await call.message.edit_text("Select one option:", reply_markup=inline.kb_bike_settings())
    else:
        async with state.proxy() as data:
            data["bike_id"] = call.data.split(":")[1]
        bike_id = call.data.split(":")[1]
        await call.message.edit_text("Select parameter which you want to update:",
                                     reply_markup=await inline.bike_parameters(bike_id))
        await UpdateBike.next()


async def update_bike_step3(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.finish()
        await update_bike(call)
    else:
        async with state.proxy() as data:
            data["parameter"] = call.data
        if call.data in ['abs_cbs', 'keyless', 'gps', 'docs']:
            await call.message.edit_text("Select new parameter:", reply_markup=inline.kb_yesno())
        elif call.data == 'color':
            await call.message.edit_text("Select new parameter:", reply_markup=inline.kb_basic_custom())
        elif call.data == 'status':
            await call.message.edit_text("Select new parameter:", reply_markup=inline.kb_bike_status())
        elif call.data in ['style', 'exhaust']:
            await call.message.edit_text("Select new parameter:", reply_markup=inline.kb_bike_style())
        elif call.data == 'photo':
            photo = await get_photo(data.get('bike_id'))
            photo_io = io.BytesIO(photo[0])
            await call.message.delete()
            await call.bot.send_photo(
                call.from_user.id,
                photo=photo_io,
                caption='Here is current photo. If you want to change it, send new one',
                reply_markup=inline.kb_cancel())
        else:
            await call.message.edit_text("Write new parameter:")
        await UpdateBike.next()


async def update_bike_step4_msg(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text:
            parameter = data.get('parameter')
            new_parameter = msg.text
            if parameter in ['purchase_price', 'mileage', 'year'] and not new_parameter.isdigit():
                await msg.answer('Please enter digits only.')
                return
            new_data = {parameter: new_parameter}
        elif msg.photo:
            file = await msg.bot.download_file_by_id(msg.photo[-1].file_id)
            photo_bytes = file.read()
            new_data = {data.get('parameter'): photo_bytes}
        else:
            return
        await db_update_bike(bike_id=data.get('bike_id'), data=new_data)
        await sheets.update_bike_sheets(data.get('bike_id'), new_data)
        await state.finish()
        await msg.answer('Bike updated. Select a bike to update:', reply_markup=await inline.kb_update_bike())
        await UpdateBike.pick.set()


async def update_bike_step4_call(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        await call.message.delete()
        await call.message.answer("Select bike for update:", reply_markup=await inline.kb_update_bike())
        await UpdateBike.pick.set()
    else:
        async with state.proxy() as data:
            if call.data in ['yes', "no"]:
                call_data = True if call.data == 'yes' else False
                data['new_parameter'] = call_data
            else:
                data["new_parameter"] = call.data
        new_data = {f"{data.get('parameter')}": f"{data.get('new_parameter')}"}
        await db_update_bike(bike_id=data.get('bike_id'), data=new_data)
        await sheets.update_bike_sheets(data.get('bike_id'), new_data)
        await state.finish()
        await call.message.delete()
        await call.message.answer('Bike updated. Select a bike to update:', reply_markup=await inline.kb_update_bike())
        await UpdateBike.pick.set()


async def change_bike_description(call: types.CallbackQuery):
    await call.message.edit_text("Select bike which description you want to change:",
                                 reply_markup=await inline.kb_delete_bike())
    await BikeDescription.bike_id.set()


async def change_bike_description_title(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.finish()
        await call.message.edit_text("Select one option:", reply_markup=inline.kb_bike_settings())
    else:
        async with state.proxy() as data:
            data["bike_id"] = call.data.split(":")[1]
        await call.message.edit_text("Input description title\n(e.g. Street bike (have mirrors):")
        await BikeDescription.next()


async def change_bike_description_power(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = msg.text
    await msg.answer("Input bike power\n(e.g. 250сс/2 cylinder/36 Horse power:")
    await BikeDescription.next()


async def change_bike_description_main(msg: types.Message, state: FSMContext):
    if msg.text.count('/') != 2:
        await msg.delete()
        await msg.answer("Please, use this template:\n(e.g. 250сс/2 cylinder/36 Horse power)")
    else:
        async with state.proxy() as data:
            data["power"] = msg.text
        await msg.answer("Input bike description\n(e.g. Very comfortable Motorcycle for every day riding. "
                         "Straight handlebar and standard (upright) riding position. "
                         "New Design. Headlamp with mono lens illuminates road perfectly.):")
        await BikeDescription.next()


async def change_bike_description_other(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = msg.text
        await msg.answer("Input any other comment\n(e.g. We speak eng,indo,rus):")
        await BikeDescription.next()


def format_number(n):
    if n >= 1000000000:
        return str(round(n / 1000000000, 1)) + ' billion'
    elif n >= 1000000:
        return str(round(n / 1000000, 1)) + ' million'
    elif n >= 1000:
        return str(n // 1000) + ' thousands'
    else:
        return str(n)


async def change_bike_description_confirm(msg: types.Message, state: FSMContext):
    await msg.answer("Preparing you description...\nPress YES, if you want to save it, "
                     "press NO, if you want to cancel operation")
    async with state.proxy() as data:
        data['other'] = msg.text
        bike_info = await get_more_bike_info(int(data.get('bike_id')))
        photo_io = io.BytesIO(bike_info[14])
        price_3 = format_number(await sheets.coefficient_math(int(data.get('bike_id')), 3))
        price_7 = format_number(await sheets.coefficient_math(int(data.get('bike_id')), 7))
        price_30 = format_number(await sheets.coefficient_math(int(data.get('bike_id')), 30))
        description_text = f"{bike_info[1]} {bike_info[2]} ({bike_info[3]})\n\n{data.get('title')}\n\n" \
                           f"{data.get('power').split('/')[0]}\n{data.get('power').split('/')[1]}\n" \
                           f"{data.get('power').split('/')[2]}\n\n{data.get('description')}\n\nPrices:\n\n" \
                           f"3 days: {price_3}\n7 days: {price_7}\n30 days: {price_30}\n\n{data.get('other')}"
        data['description'] = description_text
        await msg.answer_photo(photo=photo_io, caption=description_text, reply_markup=inline.kb_yesno())
        await BikeDescription.next()


async def change_bike_description_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as data:
            await new_description(int(data.get('bike_id')), data.get('description'))
            await call.message.delete()
            await call.message.answer("Description successfully saved!", reply_markup=inline.kb_main_menu())
            await state.finish()
    else:
        await call.message.delete()
        await call.message.answer("You canceled operation!", reply_markup=inline.kb_main_menu())
        await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main')
    dp.register_callback_query_handler(bike_settings, text="bike_settings")
    dp.register_callback_query_handler(add_new_bike_step1, text='add_new_bike')
    dp.register_message_handler(add_new_bike_step2, state=NewBike.brand)
    dp.register_message_handler(add_new_bike_step3, state=NewBike.model)
    dp.register_message_handler(add_new_bike_step3_v1, state=NewBike.year)
    dp.register_message_handler(add_new_bike_step4, state=NewBike.purchase_price)
    dp.register_message_handler(add_new_bike_step5, state=NewBike.millage)
    dp.register_callback_query_handler(add_new_bike_step6, state=NewBike.abs_cbs)
    dp.register_callback_query_handler(add_new_bike_step7, state=NewBike.keyless)
    dp.register_message_handler(add_new_bike_step8, state=NewBike.plate_no)
    dp.register_callback_query_handler(add_new_bike_step9, state=NewBike.color)
    dp.register_callback_query_handler(add_new_bike_step10, state=NewBike.gps)
    dp.register_callback_query_handler(add_new_bike_step10_v1, state=NewBike.style)
    dp.register_callback_query_handler(add_new_bike_step11, state=NewBike.docs)
    dp.register_callback_query_handler(add_new_bike_step11_2, state=NewBike.exhaust)
    dp.register_message_handler(add_new_bike_step12, state=NewBike.photo, content_types=['photo'])
    dp.register_callback_query_handler(add_new_bike_finish, state=NewBike.status)
    dp.register_callback_query_handler(add_new_another_bike, state=NewBike.another_one)
    dp.register_callback_query_handler(delete_bike_, text="delete_bike")
    dp.register_callback_query_handler(delete_confirmation, state=DeleteBike.pick)
    dp.register_callback_query_handler(delete_processing, state=DeleteBike.confirm)
    dp.register_callback_query_handler(delete_another_one, state=DeleteBike.another_one)
    dp.register_callback_query_handler(update_bike, text="change_bike_data")
    dp.register_callback_query_handler(update_bike_step2, state=UpdateBike.pick)
    dp.register_callback_query_handler(update_bike_step3, state=UpdateBike.bike_id)
    dp.register_message_handler(update_bike_step4_msg, state=UpdateBike.parameter, content_types=['text', 'photo'])
    dp.register_callback_query_handler(update_bike_step4_call, state=UpdateBike.parameter)
    dp.register_callback_query_handler(change_bike_description, text='change_bike_description')
    dp.register_callback_query_handler(change_bike_description_title, state=BikeDescription.bike_id)
    dp.register_message_handler(change_bike_description_power, state=BikeDescription.title)
    dp.register_message_handler(change_bike_description_main, state=BikeDescription.power)
    dp.register_message_handler(change_bike_description_other, state=BikeDescription.description)
    dp.register_message_handler(change_bike_description_confirm, state=BikeDescription.other)
    dp.register_callback_query_handler(change_bike_description_finish, state=BikeDescription.confirm)
