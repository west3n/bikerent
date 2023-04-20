import aiohttp
import decouple
import calendar
import datetime

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from google_json import sheets
from keyboards import inline
from database import db_service, db_admins, db_bike, db_rent, db_client


class ClientService(StatesGroup):
    service = State()
    service_id = State()
    cost = State()


class NewServiceTask(StatesGroup):
    bike_id = State()
    task = State()


class OpenTask(StatesGroup):
    service_id = State()
    service = State()
    start_month = State()
    start_day = State()


async def back_button(call: types.CallbackQuery, state: FSMContext):
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


async def check_oil_change(bike_id, oil_need_change, last_oil_change_millage, new_mileage):
    if last_oil_change_millage < 1000 < new_mileage and not oil_need_change:
        await db_service.update_oil_need_change_data(bike_id)
        service_id = await db_service.update_bike_service_status(bike_id)
        await sheets.new_task_sheets(service_id, bike_id, "oil change")
    elif last_oil_change_millage > 1000 and new_mileage > 3000 and not oil_need_change:
        await db_service.update_oil_need_change_data(bike_id)
        service_id = await db_service.update_bike_service_status(bike_id)
        await sheets.new_task_sheets(service_id, bike_id, "oil change")
    else:
        oil_change_intervals = [i * 3000 for i in range(1, 20)]
        mileage_intervals = [i * 3000 for i in range(2, 21)]
        for i, interval in enumerate(oil_change_intervals):
            if last_oil_change_millage > interval and new_mileage > mileage_intervals[i] and not oil_need_change:
                await db_service.update_oil_need_change_data(bike_id)
                service_id = await db_service.update_bike_service_status(bike_id)
                await sheets.new_task_sheets(service_id, bike_id, "oil change")
                break


async def current_services(call: types.CallbackQuery):
    await call.message.edit_text("Select one option:", reply_markup=inline.kb_current_services())


async def all_current_services(call: types.CallbackQuery):
    await call.message.edit_text("Select service:", reply_markup=await inline.kb_all_service())
    await ClientService.service.set()


async def distributor_service(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back_service':
        await state.finish()
        await current_services(call)

    elif call.data.split(":")[2] == 'client damage':
        async with state.proxy() as data:
            data.update({'service': call.data.split(":")[2],
                         'service_id': call.data.split(":")[1]})
        await call.message.edit_text("Input cost:")
        await state.set_state(ClientService.cost.state)
    elif call.data.split(":")[2] == 'oil change':
        async with state.proxy() as data:
            data.update({'service': call.data.split(":")[2],
                         'service_id': call.data.split(":")[1]})
            await call.message.edit_text("Input cost:")
            await state.set_state(ClientService.cost.state)
    else:
        async with state.proxy() as data:
            data.update({'service': call.data.split(":")[2],
                         'service_id': call.data.split(":")[1]})
            await call.message.edit_text("Input cost:")
            await state.set_state(ClientService.cost.state)


async def client_bot(client_tg, text):
    bot = Bot(decouple.config("CLIENT_BOT_TOKEN"))
    async with aiohttp.ClientSession() as session:
        await bot.send_message(chat_id=client_tg[0],
                               text=f"{text}",
                               reply_markup=inline.kb_choose_payment_method_for_client())
        session.closed


async def cost_service(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            data['cost'] = msg.text
        group_id = decouple.config("GROUP_ID")
        if data.get('service') == 'client damage':
            bike_id = await db_service.get_bike_id(int(data.get('service_id')))
            client_id = await db_rent.get_client_id_by_bike(bike_id)
            tg_id = await db_client.get_tg_id(client_id[0])
            bike = await db_bike.get_bike(bike_id)

            await msg.bot.send_message(chat_id=group_id,
                                       text=f"Task ID: {data.get('service_id')} was update!\n\n"
                                            f"Bike ID: {bike[0]} - {bike[1]}, {bike[2]}\n"
                                            f"Task: {data.get('service')}\n"
                                            f"Cost: {data.get('cost')}\n\n"
                                            f"Wait for the customer to select a payment method.")

            text = f"You must pay: {data.get('cost')} rupiah\n" \
                   f"Select a Payment Method:"
            await client_bot(tg_id, text)
            await sheets.update_task_cost_sheets(int(data.get('service_id')), data.get('cost'))
            await msg.answer("Wait for the customer to select a payment method.",
                             reply_markup=inline.kb_main_menu())
            await state.finish()
        elif data.get('service') == 'oil change':
            bike_id = await db_service.get_bike_id(int(data.get('service_id')))
            bike = await db_bike.get_bike(bike_id)
            await msg.bot.send_message(chat_id=group_id,
                                       text=f"Task ID: {data.get('service_id')} was close!\n\n"
                                            f"Bike ID: {bike[0]} - {bike[1]}, {bike[2]}\n"
                                            f"Task: {data.get('service')}\n"
                                            f"Cost: {data.get('cost')}")
            await db_service.update_oil_need_change_data_false(bike_id)
            await sheets.update_task_cost_sheets(int(data.get('service_id')), data.get('cost'))
            await db_service.delete_service(int(data.get('service_id')))
            await msg.answer(text='The task has been completed!',
                             reply_markup=inline.kb_main_menu())
            await state.finish()
        else:
            bike_id = await db_service.get_bike_id(int(data.get('service_id')))
            bike = await db_bike.get_bike(bike_id)
            await msg.bot.send_message(chat_id=group_id,
                                       text=f"Task ID: {data.get('service_id')} was close!\n\n"
                                            f"Bike ID: {bike[0]} - {bike[1]}, {bike[2]}\n"
                                            f"Task: {data.get('service').split('_')[0]}\n"
                                            f"Cost: {data.get('cost')}")
            await sheets.update_task_cost_sheets(int(data.get('service_id')), data.get('cost'))
            await db_service.delete_service(int(data.get('service_id')))
            await msg.answer(text='The task has been completed!',
                             reply_markup=inline.kb_main_menu())
            await state.finish()
    else:
        await msg.answer("Only digits! Try again:")


async def create_new_task(call: types.CallbackQuery):
    await call.message.edit_text("Select bike:", reply_markup=await inline.kb_service_bike())
    await NewServiceTask.bike_id.set()


async def select_task_data(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back_service":
        await state.finish()
        await call.message.edit_text("Select one option:", reply_markup=inline.kb_current_services())
    else:
        async with state.proxy() as data:
            data['bike_id'] = call.data.split(":")[1]
        await call.message.edit_text("Select task:", reply_markup=inline.kb_task_list())
        await NewServiceTask.next()


async def insert_new_task(call: types.CallbackQuery, state: FSMContext):
    if call.data == "other_task":
        await state.set_state(NewServiceTask.bike_id.state)
        await call.message.edit_text("Input new task (15 symbols maximum):")
        await NewServiceTask.next()
    else:
        async with state.proxy() as data:
            await call.message.edit_text("Create new task...")
            group_id = decouple.config("GROUP_ID")
            data['task'] = call.data.capitalize()
            bike_data = await db_bike.get_more_bike_info(int(data.get('bike_id')))
            service_id = await db_service.db_create_new_task(int(data.get('bike_id')), data.get('task'))
            await sheets.new_task_sheets(service_id, int(data.get('bike_id')), data.get('task'))
            await call.bot.send_message(group_id, text=f"<b>New SERVICE TASK created:</b>\n\n"
                                                       f"Bike model: {bike_data[1]} {bike_data[2]}\n"
                                                       f"Plane No: {bike_data[8]}\n"
                                                       f"Task: {data.get('task').split('_')[0]}")
            await call.message.edit_text("New task created!", reply_markup=inline.kb_main_menu())
            await state.finish()


async def insert_other_task(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        group_id = decouple.config("GROUP_ID")
        data['task'] = msg.text.capitalize()
        if len(data.get('task')) >= 15:
            await msg.delete()
            await msg.answer("15 symbols maximum! Try again!")
        else:
            answer = await msg.answer("Create new task...")
            message_id = answer.message_id
            bike_data = await db_bike.get_more_bike_info(int(data.get('bike_id')))
            service_id = await db_service.db_create_new_task(int(data.get('bike_id')), data.get('task'))
            await sheets.new_task_sheets(service_id, int(data.get('bike_id')), data.get('task'))
            await msg.bot.send_message(group_id, text=f"New task created:\n\n"
                                                      f"Bike model: {bike_data[1]} {bike_data[2]}\n"
                                                      f"Plane No: {bike_data[8]}\n"
                                                      f"Task: {data.get('task')}")
            await msg.bot.edit_message_text(chat_id=msg.chat.id, message_id=message_id, text="New task created!",
                                            reply_markup=inline.kb_main_menu())
            await state.finish()


async def client_damage_service(call: types.CallbackQuery):
    await call.message.edit_text("Select service:", reply_markup=await inline.kb_all_damage_services())
    await ClientService.service.set()


async def get_started_task(call: types.CallbackQuery):
    await call.message.edit_text("Select service:", reply_markup=await inline.kb_all_not_open_services())
    await OpenTask.service_id.set()


async def get_started_task_service(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back_service':
        await state.finish()
        await current_services(call)
    else:
        async with state.proxy() as data:
            data.update({'service_id': call.data.split(':')[1], 'service': call.data.split(':')[2]})
        print(data)
        await call.message.edit_text('Select start date:\n\nMonth:',
                                     reply_markup=inline.kb_month())
        await state.set_state(OpenTask.start_month.state)


async def get_started_task_service_month(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.finish()
        await get_started_task(call)
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
            await OpenTask.next()


async def get_started_task_service_day(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await get_started_task_service_month(call, state)
    else:
        async with state.proxy() as data:
            data['start_day'] = call.data
        await call.message.edit_text("Data successfully saved! If you want to finish task, you can make it by pressing"
                                     "'Finish service tasks' button", reply_markup=inline.kb_main_menu())
        service_id = int(data.get('service_id'))
        date_str = data.get('start_day')
        date_parts = date_str.split('_')[1:]
        year = datetime.datetime.now().year
        month, day = map(int, date_parts)
        date_obj = datetime.date(year, month, day)
        await db_service.update_open_task(date_obj, service_id)
        await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(back_button, text='back_main')
    dp.register_callback_query_handler(current_services, text=["current_services", "back_service"])
    dp.register_callback_query_handler(all_current_services, text='check_service_status')
    dp.register_callback_query_handler(create_new_task, text=['create_new_task', 'back_task'])
    dp.register_callback_query_handler(distributor_service, state=ClientService.service)
    dp.register_message_handler(cost_service, state=ClientService.cost)
    dp.register_callback_query_handler(select_task_data, state=NewServiceTask.bike_id)
    dp.register_callback_query_handler(insert_new_task, state=NewServiceTask.task)
    dp.register_message_handler(insert_other_task, state=NewServiceTask.task)
    dp.register_callback_query_handler(client_damage_service, text='task_client_damage')
    dp.register_callback_query_handler(get_started_task, text='get_started')
    dp.register_callback_query_handler(get_started_task_service, state=OpenTask.service_id)
    dp.register_callback_query_handler(get_started_task_service_month, state=OpenTask.start_month)
    dp.register_callback_query_handler(get_started_task_service_day, state=OpenTask.start_day)
