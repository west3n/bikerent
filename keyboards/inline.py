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
        [InlineKeyboardButton('Account settings', callback_data='account_settings')]
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
        [InlineKeyboardButton('Change admin roles', callback_data='change_admin_roles')]
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
