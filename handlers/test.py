from datetime import datetime, date
#
# from aiogram import Dispatcher, types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# import datetime
#
#
# def kb_month() -> InlineKeyboardMarkup:
#     months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
#               'August', 'September', 'October', 'November', 'December']
#     buttons = []
#     for i, month in enumerate(months, start=1):
#         button = InlineKeyboardButton(month, callback_data=f"month_{i}")
#         buttons.append(button)
#     calendar_keyboard = InlineKeyboardMarkup(row_width=3)
#     calendar_keyboard.add(*buttons)
#     return calendar_keyboard
#
#
#
# async def process_calendar_callback(callback_query: types.CallbackQuery):
#     _, month_number = callback_query.data.split("_")
#     days_in_month = calendar.monthrange(2023, int(month_number))[1]
#     buttons = []
#     for day in range(1, days_in_month + 1):
#         button = InlineKeyboardButton(str(day), callback_data=f"date_{month_number}_{day}")
#         buttons.append(button)
#     date_keyboard = InlineKeyboardMarkup(row_width=7)
#     date_keyboard.add(*buttons)
#     await callback_query.bot.send_message(callback_query.from_user.id, "Выберите день:", reply_markup=date_keyboard)
#
#
# async def process_date_callback(callback_query: types.CallbackQuery):
#     _, month_number, day = callback_query.data.split("_")
#     date = datetime.date(2023, int(month_number), int(day))
#     await callback_query.bot.send_message(callback_query.from_user.id, f"Выбрана дата: {date}")
#
#
# async def process_callback(callback_query: types.CallbackQuery):
#     if callback_query.data.startswith("month"):
#         await process_calendar_callback(callback_query)
#     elif callback_query.data.startswith("date"):
#         await process_date_callback(callback_query)
#
#
# def register(dp: Dispatcher):
#     dp.register_callback_query_handler(process_calendar_callback)
#     dp.register_callback_query_handler(process_callback)

def test():
    date_str = 'date_3_12'
    date_parts = date_str.split('_')[1:]
    year = datetime.now().year
    month, day = map(int, date_parts)
    date_obj = date(year, month, day)
    print(date_obj)

test()