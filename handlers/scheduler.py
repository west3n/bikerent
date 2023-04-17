import decouple
from aiogram import Bot
import asyncio
import datetime
from database import db_booking, db_service, db_rent


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
            msg = await db_booking.send_daily_deliveries()
            await send_message_daily(msg)
            print(f"send_daily_deliveries completed at {datetime.datetime.now()}")
        if now.hour == 7 and now.minute == 00:
            msg = await db_service.send_service_notification()
            await send_message_daily(msg)
            print(f"send_service_notification completed at {datetime.datetime.now()}")
        if now.hour == 7 and now.minute == 10:
            msg = await db_rent.select_rental_by_date_finish_today()
            await send_message_daily(msg)
            print(f"select_rental_by_date_finish_today completed at {datetime.datetime.now()}")
        if now.hour == 9 and now.minute == 00:
            msg = await db_rent.select_rental_by_date_finish_two_days_from_now()
            await send_message_daily(msg)
            print(f"select_rental_by_date_finish_two_days_from_now completed at {datetime.datetime.now()}")
        await asyncio.sleep(60 - now.second)


if __name__ == '__main__':
    asyncio.run(run_daily_task())
