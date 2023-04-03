from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database import db_admins, postgresql
from keyboards import inline


class NewAdmin(StatesGroup):
    tg_id = State()
    name = State()
    status = State()


class UpdateRole(StatesGroup):
    tg_id = State()
    status = State()


async def account_settings(call: types.CallbackQuery):
    await call.message.edit_text(text="Account settings", reply_markup=inline.kb_account_settings())


async def new_admin_account_tg_id(call: types.CallbackQuery):
    await call.message.edit_text("Input Telegram ID:")
    await NewAdmin.tg_id.set()


async def new_admin_account_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tg_id'] = msg.text
    await msg.answer("Input Name:")
    await NewAdmin.next()


async def new_admin_account_status(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await msg.answer("Choose admin status:", reply_markup=inline.kb_admin_status())
    await NewAdmin.next()


async def new_admin_account_finish(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['status'] = call.data
    await call.message.edit_text("Registration complete!")
    try:
        await db_admins.create_admin(data)
    except:
        await call.message.edit_text("Admin already exist!")
        postgresql.db.rollback()
    await state.finish()


async def delete_admin_account(call: types.CallbackQuery):
    admins = await db_admins.all_admins()
    if admins:
        await call.message.edit_text("Pick admin account:",
                                     reply_markup=await inline.kb_all_admins(admins))
    else:
        await call.message.edit_text("You have no admin accounts!")


async def delete_admin_account_finish(call: types.CallbackQuery):
    await db_admins.delete_admin(int(call.data.split(":")[1]))
    await call.message.edit_text(f"Account successfully deleted!")


async def change_admin_roles(call: types.CallbackQuery):
    admins = await db_admins.all_admins()
    if admins:
        await call.message.edit_text("Pick admin account:",
                                     reply_markup=await inline.kb_all_admins_2(admins))
        await UpdateRole.tg_id.set()
    else:
        await call.message.edit_text("You have no admin accounts!")


async def change_admin_roles_step1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["tg_id"] = call.data.split(":")[1]
    await call.message.edit_text("Pick new role:", reply_markup=inline.kb_admin_status())
    await UpdateRole.next()


async def change_admin_roles_finish(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['status'] = call.data
    await db_admins.update_admin(data)
    await call.message.edit_text("Admin role successfully updated!")
    await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(account_settings, text='account_settings')
    dp.register_callback_query_handler(new_admin_account_tg_id, text='new_admin_account')
    dp.register_message_handler(new_admin_account_name, state=NewAdmin.tg_id)
    dp.register_message_handler(new_admin_account_status, state=NewAdmin.name)
    dp.register_callback_query_handler(new_admin_account_finish, state=NewAdmin.status)
    dp.register_callback_query_handler(delete_admin_account, text='delete_admin_account')
    dp.register_callback_query_handler(delete_admin_account_finish, lambda c: c.data.startswith("delete:"))
    dp.register_callback_query_handler(change_admin_roles, text='change_admin_roles')
    dp.register_callback_query_handler(change_admin_roles_step1, state=UpdateRole.tg_id)
    dp.register_callback_query_handler(change_admin_roles_finish, state=UpdateRole.status)
