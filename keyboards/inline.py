from datetime import timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from database.db_bike import get_bike_info, get_more_bike_info, get_bike, get_bike_booking_status, \
    get_all_bikes_description
from database.db_booking import check_booking, all_bookings
from database.db_rent import all_rent
from database.db_service import get_open_service, get_client_damage_service, get_not_opened_service


def start_superuser() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Information', callback_data='information')],
        [InlineKeyboardButton('New booking', callback_data='new_booking')],
        [InlineKeyboardButton('Extend current rental', callback_data='extend_current_rental')],
        [InlineKeyboardButton('Cancel booking', callback_data='cancel_booking')],
        [InlineKeyboardButton('Delivery', callback_data='delivery')],
        [InlineKeyboardButton('Current services', callback_data='current_services')],
        [InlineKeyboardButton('Finish rent', callback_data='finish_rent')],
        [InlineKeyboardButton('Account settings', callback_data='account_settings')],
        [InlineKeyboardButton('Bike settings', callback_data='bike_settings')]
    ])
    return kb


def start_manager() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Information', callback_data='information')],
        [InlineKeyboardButton('New booking', callback_data='new_booking')],
        [InlineKeyboardButton('Extend current rental', callback_data='extend_current_rental')],
        [InlineKeyboardButton('Cancel booking', callback_data='cancel_booking')],
        [InlineKeyboardButton('Delivery', callback_data='delivery')],
        [InlineKeyboardButton('Current services', callback_data='current_services')],
        [InlineKeyboardButton('Finish rent', callback_data='finish_rent')]
    ])
    return kb


def start_deliveryman() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Delivery', callback_data='delivery')],
        [InlineKeyboardButton('Current services', callback_data='current_services')],
        [InlineKeyboardButton('Finish rent', callback_data='finish_rent')]
    ])
    return kb


def kb_account_settings() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Enter new admin', callback_data='new_admin_account')],
        [InlineKeyboardButton('Delete admin account', callback_data='delete_admin_account')],
        [InlineKeyboardButton('Change admin roles', callback_data='change_admin_roles')],
        [InlineKeyboardButton('Back to main menu', callback_data='back_main')]
    ])
    return kb


def kb_admin_status() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Supervisor', callback_data='supervisor')],
        [InlineKeyboardButton('Manager', callback_data='manager')]
    ])
    return kb


async def kb_all_admins(admins) -> InlineKeyboardMarkup:
    admin_callback = CallbackData("delete", "tg_id")
    kb = InlineKeyboardMarkup()
    for admin in admins:
        button = InlineKeyboardButton(text=f'name: {admin[1]}, status: {admin[2].capitalize()}',
                                      callback_data=admin_callback.new(tg_id=admin[0]))
        kb.add(button)
    return kb


async def kb_all_admins_2(admins) -> InlineKeyboardMarkup:
    admin_callback = CallbackData("update", "tg_id")
    kb = InlineKeyboardMarkup()
    for admin in admins:
        button = InlineKeyboardButton(text=f'name: {admin[1]}, status: {admin[2].capitalize()}',
                                      callback_data=admin_callback.new(tg_id=admin[0]))
        kb.add(button)
    return kb


def kb_bike_settings() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Add new bike', callback_data='add_new_bike')],
        [InlineKeyboardButton('Change bike data', callback_data='change_bike_data')],
        [InlineKeyboardButton('Change bike description', callback_data='change_bike_description')],
        [InlineKeyboardButton('Delete bike', callback_data='delete_bike')],
        [InlineKeyboardButton('Back to main menu', callback_data='back_main')]
    ])
    return kb


def kb_yesno() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Yes', callback_data='yes')],
        [InlineKeyboardButton('No', callback_data='no')]
    ])
    return kb


def kb_basic_custom() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Basic', callback_data='basic')],
        [InlineKeyboardButton('Custom', callback_data='custom')]
    ])
    return kb


def kb_bike_status() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Free', callback_data='free')],
        [InlineKeyboardButton('Booking', callback_data='booking')],
        [InlineKeyboardButton('Rent', callback_data='rent')],
    ])
    return kb


async def kb_delete_bike() -> InlineKeyboardMarkup:
    bikes = await get_bike_info()
    bike_callback = CallbackData("delete_bike", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back')
    kb.add(back)
    return kb


async def kb_update_bike() -> InlineKeyboardMarkup:
    bikes = await get_bike_info()
    bike_callback = CallbackData("update_bike", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back')
    kb.add(back)
    return kb


async def bike_parameters(bike_id) -> InlineKeyboardMarkup:
    bike = await get_more_bike_info(bike_id)
    abs_cbs = "Yes" if bike[6] else "No"
    keyless = "Yes" if bike[7] else "No"
    gps = "Yes" if bike[10] else "No"
    docs = "Yes" if bike[12] else "No"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'Brand: {bike[1]}', callback_data='brand')],
        [InlineKeyboardButton(f'Model: {bike[2]}', callback_data='model')],
        [InlineKeyboardButton(f'Year: {bike[3]}', callback_data='year')],
        [InlineKeyboardButton(f'Purchase price: {bike[4]}', callback_data='purchase_price')],
        [InlineKeyboardButton(f'Millage: {bike[5]}', callback_data='millage')],
        [InlineKeyboardButton(f'ABS/CBS: {abs_cbs}', callback_data='abs_cbs')],
        [InlineKeyboardButton(f'Keyless: {keyless}', callback_data='keyless')],
        [InlineKeyboardButton(f'Plate No: {bike[8]}', callback_data='plate_no')],
        [InlineKeyboardButton(f'Color: {bike[9].capitalize()}', callback_data='color')],
        [InlineKeyboardButton(f'GPS: {gps}', callback_data='gps')],
        [InlineKeyboardButton(f'Style: {bike[11].capitalize()}', callback_data='style')],
        [InlineKeyboardButton(f'Document on hand: {docs}', callback_data='docs')],
        [InlineKeyboardButton(f'Exhaust: {bike[13].capitalize()}', callback_data='exhaust')],
        [InlineKeyboardButton(f'Status: {bike[15].capitalize()}', callback_data='status')],
        [InlineKeyboardButton(f'Photo', callback_data='photo')],
        [InlineKeyboardButton('Back', callback_data='back')]
    ])
    return kb


def kb_cancel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Cancel', callback_data='cancel')]
    ])
    return kb


def kb_main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Back to main menu', callback_data='back_main')]
    ])
    return kb


async def kb_booking_bike() -> InlineKeyboardMarkup:
    bikes = await get_bike_info()
    bike_callback = CallbackData("booking", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_main')
    kb.add(back)
    return kb


async def kb_delivery_bike() -> InlineKeyboardMarkup:
    bikes = await get_bike_booking_status()
    bike_callback = CallbackData("booking", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_main')
    kb.add(back)
    return kb


def kb_month() -> InlineKeyboardMarkup:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    buttons = []
    for i, month in enumerate(months, start=1):
        button = InlineKeyboardButton(month, callback_data=f"month_{i}")
        buttons.append(button)
    calendar_keyboard = InlineKeyboardMarkup(row_width=3)
    calendar_keyboard.add(*buttons)
    previous_step = InlineKeyboardButton("Back", callback_data="back")
    calendar_keyboard.add(previous_step)
    return calendar_keyboard


def kb_rental_period() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Daily', callback_data='1_day')],
        [InlineKeyboardButton('Weekly', callback_data='1_week')],
        [InlineKeyboardButton('Monthly', callback_data='1_month')],
        [InlineKeyboardButton('Other period', callback_data='other_period')],
        [InlineKeyboardButton('Back', callback_data='back')]
    ])
    return kb


def kb_bike_style() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Stock', callback_data='stock')],
        [InlineKeyboardButton('Custom', callback_data='custom')],
    ])
    return kb


def press_x_to_win() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Info for deliveryman', callback_data='press_x')]
    ])
    return kb


async def kb_cancel_booking(bike_id) -> InlineKeyboardMarkup:
    bookings = await check_booking(bike_id)
    if bookings:
        booking_callback = CallbackData("booking_cancel", "id")
        kb = InlineKeyboardMarkup()
        for booking in bookings:
            start_date = booking[2].strftime("%d.%m.%Y")
            end_date = (booking[2] + timedelta(days=int(booking[3]))).strftime("%d.%m.%Y")
            button = InlineKeyboardButton(text=f'ID: {booking[0]} - Start: {start_date}, End: {end_date}',
                                          callback_data=booking_callback.new(id=f'{booking[0]}'))
            kb.add(button)
        previous_step = InlineKeyboardButton(text="Back", callback_data="back")
        kb.add(previous_step)
        return kb
    else:
        kb = InlineKeyboardMarkup()
        return_to_menu = InlineKeyboardButton(text="Return to main menu", callback_data="back_main")
        kb.add(return_to_menu)
        return kb


async def kb_start_delivery(bike_id) -> InlineKeyboardMarkup:
    bookings = await check_booking(bike_id)
    if bookings:
        booking_callback = CallbackData("delivery", "id")
        kb = InlineKeyboardMarkup()
        for booking in bookings:
            datetime_obj = booking[7]
            output_date = datetime_obj.strftime('%H:%M %d.%m.%Y')
            button = InlineKeyboardButton(text=f'ID: {booking[0]} -  Delivery time: {output_date}',
                                          callback_data=booking_callback.new(id=f'{booking[0]}'))
            kb.add(button)
        previous_step = InlineKeyboardButton(text="Back", callback_data="back")
        kb.add(previous_step)
        return kb
    else:
        kb = InlineKeyboardMarkup()
        return_to_menu = InlineKeyboardButton(text="Return to main menu", callback_data="back_main")
        kb.add(return_to_menu)
        return kb


def kb_payment_method() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Transfer', callback_data='transfer')],
        [InlineKeyboardButton('Crypto', callback_data='crypto')],
        [InlineKeyboardButton('Cash', callback_data='cash')]
    ])
    return kb


async def kb_all_rent() -> InlineKeyboardMarkup:
    rents = await all_rent()
    rent_callback = CallbackData("rent", "id")

    kb = InlineKeyboardMarkup()
    for rent in rents:
        bike = await get_bike(rent[1])
        button = InlineKeyboardButton(text=f'Bike: {bike[1]} ({bike[2]}), Rent end: {rent[4].strftime("%d.%m.%Y")}',
                                      callback_data=rent_callback.new(id=rent[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_main')
    kb.add(back)
    return kb


async def kb_all_bookings() -> InlineKeyboardMarkup:
    bookings = await all_bookings()
    rent_callback = CallbackData("booking", "id")
    kb = InlineKeyboardMarkup()
    for booking in bookings:
        bike = await get_bike(booking[1])
        button = InlineKeyboardButton(text=f'Bike ID: {bike[0]}, Model: {bike[1]} ({bike[2]})',
                                      callback_data=rent_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_main')
    kb.add(back)
    return kb


def kb_confirm_qr() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Confirm', callback_data='confirm_qr')]
    ])
    return kb


def kb_information() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Check bike price', callback_data='check_bike_price')],
        [InlineKeyboardButton('Check available bikes', callback_data='check_available_bikes')],
        [InlineKeyboardButton('Check rental status', callback_data='check_rental_status')],
        [InlineKeyboardButton('Create new post', callback_data='create_new_post')],
        [InlineKeyboardButton('Back', callback_data='back_main')]
    ])
    return kb


def kb_info_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Back', callback_data='info_back')]
    ])
    return kb


def kb_info_back_1() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Back', callback_data='info_back_1')]
    ])
    return kb


def kb_info_back_2() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Back', callback_data='info_back_2')]
    ])
    return kb


def booking_rent() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Booking', callback_data='info_booking')],
        [InlineKeyboardButton('Rent', callback_data='info_rent')],
        [InlineKeyboardButton('Back', callback_data='info_back_1')]
    ])
    return kb


def kb_current_services() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Create new task', callback_data='create_new_task')],
        [InlineKeyboardButton('Finish service task', callback_data='check_service_status')],
        [InlineKeyboardButton('Get started with task', callback_data='get_started')],
        [InlineKeyboardButton('Client damage', callback_data='task_client_damage')],
        [InlineKeyboardButton('Back', callback_data='back_main')]
    ])
    return kb


async def kb_all_service() -> InlineKeyboardMarkup:
    services = await get_open_service()
    services_callback = CallbackData("service_distrib", "id", "status")
    kb = InlineKeyboardMarkup()
    for service in services:
        bike = await get_bike(service[1])
        button = InlineKeyboardButton(text=f"ID {service[0]} - Bike: {bike[2]}: {service[4].split('_')[0].capitalize()}",
                                      callback_data=services_callback.new(id=service[0], status=service[4]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_service')
    kb.add(back)
    return kb


async def kb_all_damage_services() -> InlineKeyboardMarkup:
    services = await get_client_damage_service()
    services_callback = CallbackData("service_distrib", "id", "status")
    kb = InlineKeyboardMarkup()
    for service in services:
        bike = await get_bike(service[1])
        button = InlineKeyboardButton(text=f"ID {service[0]} - Bike: {bike[2]}: {service[4].capitalize()}",
                                      callback_data=services_callback.new(id=service[0], status=service[4]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_service')
    kb.add(back)
    return kb


async def kb_all_not_open_services() -> InlineKeyboardMarkup:
    services = await get_not_opened_service()
    print(services)
    services_callback = CallbackData("service_distrib", "id", "status")
    kb = InlineKeyboardMarkup()
    for service in services:
        bike = await get_bike(service[1])
        button = InlineKeyboardButton(text=f"ID {service[0]} - Bike: {bike[2]}: {service[4].capitalize()}",
                                      callback_data=services_callback.new(id=service[0], status=service[4]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_service')
    kb.add(back)
    return kb


async def kb_service_bike() -> InlineKeyboardMarkup:
    bikes = await get_bike_info()
    bike_callback = CallbackData("service_bike", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_service')
    kb.add(back)
    return kb


def kb_task_list() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Brakes', callback_data='brakes_task')],
        [InlineKeyboardButton('Filters', callback_data='filters_task')],
        [InlineKeyboardButton('Wash', callback_data='wash_task')],
        [InlineKeyboardButton('Repair', callback_data='repair_task')],
        [InlineKeyboardButton('Other', callback_data='other_task')],
        [InlineKeyboardButton('Back', callback_data='back_task')]
    ])
    return kb


def kb_choose_payment_method_for_client() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Choose payment method', callback_data='choose_method')]
    ])
    return kb


async def kb_description_bike() -> InlineKeyboardMarkup:
    bikes = await get_all_bikes_description()
    bike_callback = CallbackData("description", "id")
    kb = InlineKeyboardMarkup()
    for bike in bikes:
        await get_more_bike_info(bike[0])
        button = InlineKeyboardButton(text=f'ID:{bike[0]}, Model: {bike[1]}, NO: {bike[2]}',
                                      callback_data=bike_callback.new(id=bike[0]))
        kb.add(button)
    back = InlineKeyboardButton(text='Back', callback_data='back_description')
    kb.add(back)
    return kb
