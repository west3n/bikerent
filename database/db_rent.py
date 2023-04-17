import datetime
from datetime import timedelta

from database import db_bike, db_client
from database.postgresql import db, cur
from database.db_booking import status_booking


async def add_new_rent(booking_id):
    info = await status_booking(booking_id)
    bike_id = info[1]
    client_id = info[5]
    start_date = info[2]
    end_date = (info[2] + timedelta(days=info[3])).strftime("%Y-%m-%d")
    cur.execute("INSERT INTO rent (bike, client, date_start, date_finish) VALUES (%s, %s, %s, %s)",
                (bike_id, client_id, start_date, end_date))
    db.commit()


async def get_all_rent(bike_id):
    cur.execute("SELECT * FROM rent WHERE bike=%s", (bike_id,))
    result = cur.fetchall()
    return result


async def get_all_rent_info(bike_id):
    cur.execute("SELECT * FROM rent WHERE bike=%s", (bike_id,))
    result = cur.fetchone()
    return result


async def get_bike_id(rent_id):
    cur.execute("SELECT bike FROM rent WHERE id=%s", (rent_id,))
    result = cur.fetchone()
    return result


async def all_rent():
    cur.execute("SELECT * FROM rent")
    result = cur.fetchall()
    return result


async def finish_rent(rent_id):
    cur.execute("DELETE FROM rent WHERE id=%s", (rent_id,))
    db.commit()


async def gen_end_date(rent_id):
    cur.execute("SELECT date_finish FROM rent WHERE id=%s", (rent_id,))
    result = cur.fetchone()
    return result


async def update_date(rent_id, date_finish):
    cur.execute("UPDATE rent SET date_finish = %s WHERE id=%s", (date_finish, rent_id,))
    db.commit()


async def get_client_id(rent_id):
    cur.execute("SELECT client FROM rent WHERE id=%s", (rent_id,))
    result = cur.fetchone()
    return result


async def get_client_id_by_bike(bike_id):
    cur.execute("SELECT client FROM rent WHERE bike=%s", (bike_id,))
    result = cur.fetchone()
    return result


async def select_rental_by_date_finish_today():
    today = datetime.datetime.now().date()
    cur.execute("SELECT * FROM rent WHERE date_finish = %s", (today,))
    rows = cur.fetchall()
    message = f"RENT FINISH TODAY:\n" \
              f"Contact the client and make an appointment to pick up the bike\n"
    if rows:
        for result in rows:
            bike = await db_bike.get_bike(result[1])
            client_contact = await db_client.get_client_contact(result[2])
            message += f"\n- Rent #{result[0]}\n finished today!" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Client contact: {client_contact[0]}"

    else:
        message = 'There are no ending rents today!'
    return message


async def select_rental_by_date_finish_two_days_from_now():
    two_days_from_now = datetime.datetime.now().date() + datetime.timedelta(days=2)
    cur.execute("SELECT * FROM rent WHERE date_finish = %s", (two_days_from_now,))
    rows = cur.fetchall()
    message = f"RENT FINISH 2 DAYS LATER :\n" \
              f"Contact the client to clarify the rent extension. If not, make an appointment to return the bike\n"
    if rows:
        for result in rows:
            bike = await db_bike.get_bike(result[1])
            client_contact = await db_client.get_client_contact(result[2])
            message += f"\n- Rent #{result[0]}\n finished 2 days later!" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Client contact: {client_contact[0]}"

    else:
        message = 'There are no ending rents!'
    return message
