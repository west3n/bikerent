from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from database.db_bike import get_bike_info, get_more_bike_info


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
        [InlineKeyboardButton('Manager', callback_data='manager')],
        [InlineKeyboardButton('Deliveryman', callback_data='deliveryman')]
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
        button = InlineKeyboardButton(text=f'model: {bike[1]}, plate NO: {bike[2]}',
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
        button = InlineKeyboardButton(text=f'model: {bike[1]}, plate NO: {bike[2]}',
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
        button = InlineKeyboardButton(text=f'model: {bike[1]}, plate NO: {bike[2]}',
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
    return calendar_keyboard


def kb_rental_period() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Daily', callback_data='1_day')],
        [InlineKeyboardButton('Weekly', callback_data='1_week')],
        [InlineKeyboardButton('Monthly', callback_data='1_month')],
        [InlineKeyboardButton('Other period', callback_data='other_period')]
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
