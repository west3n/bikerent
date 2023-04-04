from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


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
    abs_cbs = "Yes" if bike[5] else "No"
    keyless = "Yes" if bike[6] else "No"
    gps = "Yes" if bike[9] else "No"
    docs = "Yes" if bike[10] else "No"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'Brand: {bike[1]}', callback_data='brand')],
        [InlineKeyboardButton(f'Model: {bike[2]}', callback_data='model')],
        [InlineKeyboardButton(f'Purchase price: {bike[3]}', callback_data='purchase_price')],
        [InlineKeyboardButton(f'Millage: {bike[4]}', callback_data='millage')],
        [InlineKeyboardButton(f'ABS/CBS: {abs_cbs}', callback_data='abs_cbs')],
        [InlineKeyboardButton(f'Keyless: {keyless}', callback_data='keyless')],
        [InlineKeyboardButton(f'Plate No: {bike[7]}', callback_data='plate_no')],
        [InlineKeyboardButton(f'Color: {bike[8].capitalize()}', callback_data='color')],
        [InlineKeyboardButton(f'GPS: {gps}', callback_data='gps')],
        [InlineKeyboardButton(f'Document on hand: {docs}', callback_data='docs')],
        [InlineKeyboardButton(f'Status: {bike[12].capitalize()}', callback_data='status')],
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
