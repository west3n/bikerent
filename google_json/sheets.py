import gspread
import math
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
