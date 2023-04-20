import decouple
import psycopg2
from aiogram import Bot
import asyncio
import datetime
from database import db_booking, db_service, db_rent

db = psycopg2.connect(
    host="92.53.127.97",
    database="default_db",
    user="gen_user",
    password="Tim262Tim262"
)

cur = db.cursor()


async def get_bike(bike_id):
    query = "SELECT id, model, plate_no FROM bike WHERE id=%s"
    values = (bike_id,)
    cur.execute(query, values)
    results = cur.fetchone()
    return results


async def get_client_contact(client_id):
    cur.execute("SELECT contact FROM client WHERE id=%s", (client_id,))
    result = cur.fetchone()
    return result


async def send_daily_deliveries():
    now = datetime.datetime.now()
    query = """
        SELECT *
        FROM booking
        WHERE start_date = %s
    """
    cur.execute(query, (now.date(),))
    results = cur.fetchall()
    message = f"DELIVERY TASK TODAY: ({now.date().strftime('%d.%m.%Y')}):\n"
    if results:
        for result in results:
            bike = await get_bike(result[1])
            client_contact = await get_client_contact(result[5])
            message += f"\n- Delivery #{result[0]}: {result[7]} (Delivery price: {result[8]} rupiah.)\n\n" \
                       f"Rent price: {result[9]}\n" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Address: {result[6]}\n" \
                       f"Client contact: {client_contact[0]}"
    else:
        message += f"\nNo delivery today =("

    return message


async def send_service_notification():
    query = """
            SELECT *
            FROM service
        """
    cur.execute(query)
    results = cur.fetchall()
    message = f"SERVICE TASKS NOT CLOSED:\n"
    if results:
        for result in results:
            bike = await get_bike(result[1])
            message += f"\n- Service task #{result[0]}\n" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Task: {result[2]}\n"

    else:
        message = 'Today very good day:\n' \
                  'No service tasks!'

    return message


async def select_rental_by_date_finish_two_days_from_now():
    two_days_from_now = datetime.datetime.now().date() + datetime.timedelta(days=2)
    cur.execute("SELECT * FROM rent WHERE date_finish = %s", (two_days_from_now,))
    rows = cur.fetchall()
    message = f"RENT FINISH 2 DAYS LATER :\n" \
              f"Contact the client to clarify the rent extension. If not, make an appointment to return the bike\n"
    if rows:
        for result in rows:
            bike = await get_bike(result[1])
            client_contact = await get_client_contact(result[2])
            message += f"\n- Rent #{result[0]}\n finished 2 days later!" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Client contact: {client_contact[0]}"

    else:
        message = 'There are no ending rents!'
    return message


async def select_rental_by_date_finish_today():
    today = datetime.datetime.now().date()
    cur.execute("SELECT * FROM rent WHERE date_finish = %s", (today,))
    rows = cur.fetchall()
    message = f"RENT FINISH TODAY:\n" \
              f"Contact the client and make an appointment to pick up the bike\n"
    if rows:
        for result in rows:
            bike = await get_bike(result[1])
            client_contact = await get_client_contact(result[2])
            message += f"\n- Rent #{result[0]}\n finished today!" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Client contact: {client_contact[0]}"

    else:
        message = 'There are no ending rents today!'
    return message


async def send_message_daily(msg):
    bot = Bot.get_current()
    if bot is None:
        bot = Bot(token=decouple.config('BOT_TOKEN'))
        Bot.set_current(bot)
    await bot.send_message(chat_id=decouple.config('GROUP_ID'),
                           text=msg)


async def run_daily_task():
    print(f"Scheduler run at {datetime.datetime.now()}")
    while True:
        now = datetime.datetime.now()
        if now.hour == 6 and now.minute == 30:
            msg = await send_daily_deliveries()
            await send_message_daily(msg)
            print(f"send_daily_deliveries completed at {datetime.datetime.now()}")
        if now.hour == 7 and now.minute == 00:
            msg = await send_service_notification()
            await send_message_daily(msg)
            print(f"send_service_notification completed at {datetime.datetime.now()}")
        if now.hour == 7 and now.minute == 10:
            msg = await select_rental_by_date_finish_today()
            await send_message_daily(msg)
            print(f"select_rental_by_date_finish_today completed at {datetime.datetime.now()}")
        if now.hour == 9 and now.minute == 00:
            msg = await select_rental_by_date_finish_two_days_from_now()
            await send_message_daily(msg)
            print(f"select_rental_by_date_finish_two_days_from_now completed at {datetime.datetime.now()}")
        await asyncio.sleep(60 - now.second)


if __name__ == '__main__':
    asyncio.run(run_daily_task())
