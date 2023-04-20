import gspread
import math
from datetime import datetime, date
from decouple import config
from oauth2client.service_account import ServiceAccountCredentials
from database.db_bike import get_more_bike_info

credentials_path = "google_json/true-cost-bali-a481b19b2b8f.json"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_url(config("SHEET_URL"))


def calculate_price(day_price, week_price, month_price, num_days):
    if num_days < 7:
        return day_price * num_days
    elif num_days < 30:
        num_weeks = num_days // 7
        extra_days = num_days % 7
        return week_price * num_weeks + day_price * extra_days
    else:
        num_months = num_days // 30
        extra_days = num_days % 30
        return month_price * num_months + week_price * (extra_days // 7) + day_price * (extra_days % 7)


async def coefficient_math(bike_id, num_days):
    bike_info = await get_more_bike_info(bike_id)
    bike_model = bike_info[2]
    bike_millage = bike_info[5]
    bike_year = bike_info[3]
    bike_color = bike_info[9]
    bike_style = bike_info[11]
    bike_abs = bike_info[6]
    bike_exhaust = bike_info[13]
    worksheet = gc.open_by_url(config("SHEET_URL")).worksheet("Price calc")
    search_value = bike_model
    cell = worksheet.find(search_value)
    row = worksheet.row_values(cell.row)
    monthly_price = int(row[3])
    weekly_price = math.ceil((monthly_price / 3.2) / 10000) * 10000
    daily_price = weekly_price / 5
    if int(bike_millage) < 5000:
        mileage_factor = float(row[4].replace(",", "."))
    elif 5000 < int(bike_millage) < 10000:
        mileage_factor = float(row[5].replace(",", "."))
    elif 10000 < int(bike_millage) < 20000:
        mileage_factor = float(row[6].replace(",", "."))
    else:
        mileage_factor = float(row[7].replace(",", "."))

    if bike_color == 'basic':
        color_factor = float(row[8].replace(",", "."))
    elif bike_color == 'custom':
        color_factor = float(row[9].replace(",", "."))
    else:
        color_factor = 1

    if str(bike_year) == "2022":
        year_factor = float(row[10].replace(",", "."))
    elif str(bike_year) == "2023":
        year_factor = float(row[11].replace(",", "."))
    elif str(bike_year) == "2024":
        year_factor = float(row[12].replace(",", "."))
    elif str(bike_year) == "2025":
        year_factor = float(row[13].replace(",", "."))
    else:
        year_factor = 1

    abs_factor = float(row[14].replace(",", ".")) if bike_abs else 1

    if bike_style == "stock":
        style_factor = float(row[15].replace(",", "."))
    elif bike_style == "custom":
        style_factor = float(row[16].replace(",", "."))
    else:
        style_factor = 1
    if bike_exhaust == "stock":
        exhaust_factor = float(row[17].replace(",", "."))
    elif bike_exhaust == 'custom':
        exhaust_factor = float(row[18].replace(",", "."))
    else:
        exhaust_factor = 1
    daily_price *= mileage_factor * color_factor * year_factor * abs_factor * style_factor * exhaust_factor
    weekly_price *= mileage_factor * color_factor * year_factor * abs_factor * style_factor * exhaust_factor
    monthly_price *= mileage_factor * color_factor * year_factor * abs_factor * style_factor * exhaust_factor
    custom_days_price = math.ceil(calculate_price(daily_price, weekly_price, monthly_price, num_days) / 1000) * 1000
    return custom_days_price


async def new_bike_sheets(data, bike_id):
    worksheet_name = 'bot_bikes'
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=worksheet_name, rows=100, cols=20)
    keys = ['brand', 'model', 'year', 'purchase_price', 'millage', 'abs_cbs', 'keyless', 'plate_no',
            'color', 'gps', 'style', 'docs', 'exhaust', 'status']
    row = [data.get(key) for key in keys]
    row.insert(0, bike_id)
    row_num = 2
    for col_num, cell_value in enumerate(row):
        worksheet.update_cell(row_num, col_num + 1, cell_value)


async def update_bike_sheets(bike_id, data):
    worksheet_name = 'bot_bikes'
    worksheet = sh.worksheet(worksheet_name)
    row_num = worksheet.find(bike_id).row
    header_row = worksheet.row_values(1)
    for key, value in data.items():
        if key == 'millage':
            key = 'Mileage'
        elif key in ["gps", "abs_cbs"]:
            key = key.upper()
        elif key == 'plate_no':
            key = "Plate No"
        else:
            key = key.capitalize()
        if value == "True":
            value = 'yes'
        elif value == "False":
            value = 'no'
        else:
            value = value
        col_num = header_row.index(key) + 1
        worksheet.update_cell(row_num, col_num, value)


async def delete_bike_sheets(bike_id):
    worksheet_name = 'bot_bikes'
    worksheet = sh.worksheet(worksheet_name)
    row_num = worksheet.find(bike_id).row
    worksheet.delete_row(row_num)


async def add_booking_sheets(booking_id, data):
    print(booking_id, data)
    worksheet_name = 'bot_bookings'
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=worksheet_name, rows=100, cols=20)
    keys = ['bike', 'start_day', 'rental_period', 'client_id', 'address', 'delivery_time', 'delivery_price',
            'price', 'discount', 'booking_comment']
    row = [data.get(key) for key in keys]
    rental_period = data.get('rental_period')
    if not rental_period.isdigit():
        if rental_period == '1_day':
            rental_period = 1
        elif rental_period == '1_week':
            rental_period = 7
        elif rental_period == '1_month':
            rental_period = 30
    row[keys.index('rental_period')] = rental_period
    date_str = data.get('start_day')
    date_parts = date_str.split('_')[1:]
    year = datetime.now().year
    month, day = map(int, date_parts)
    date_obj = date(year, month, day)
    time_obj = datetime.strptime(data.get('delivery_time'), '%H:%M').time()
    datetime_obj = datetime.combine(date_obj, time_obj)
    formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M')
    row[1] = date_obj.strftime('%Y-%m-%d')
    row[5] = formatted_datetime
    row.insert(0, booking_id)
    row_num = 2
    for col_num, cell_value in enumerate(row):
        worksheet.update_cell(row_num, col_num + 1, cell_value)


async def new_task_sheets(service_id, bike_id, task):
    worksheet_name = 'bot_tasks'
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=worksheet_name, rows=100, cols=20)
    header_row = worksheet.row_values(1)
    if not header_row:
        header_row = ['service_id', 'bike_id', 'task']
        worksheet.append_row(header_row)
    row = [service_id, bike_id, task]
    worksheet.append_row(row)


async def update_task_cost_sheets(service_id, cost):
    worksheet_name = 'bot_tasks'
    worksheet = sh.worksheet(worksheet_name)
    header_row = worksheet.row_values(1)
    col_num = header_row.index('Cost') + 1
    cell = worksheet.find(str(service_id))
    row_num = cell.row
    worksheet.update_cell(row_num, col_num, cost)
